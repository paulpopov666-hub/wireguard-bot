from loguru import logger
from os import remove
from io import BytesIO
from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.utils.markdown import hcode, hlink

from middlewares import rate_limit
import keyboards as kb

import database
from loader import bot
from data import configuration
from loader import vpn_config
from database import selector

from utils.fsm import NewConfig, NewPayment
from utils.qr_code import create_qr_code_from_peer_data


@rate_limit(limit=5)
async def cmd_start(message: types.Message) -> types.Message:
    if not message.from_user.username:
        await message.answer(
            f"Привет, {message.from_user.full_name}!\nУ тебя не установлен username, установи его в настройках телеграма и напиши /start\n"
            f"Если не знаешь как это сделать - посмотри {hlink('справку', 'https://silverweb.by/kak-sozdat-nik-v-telegramm/')}",
            parse_mode=types.ParseMode.HTML,
        )
        return
    
    # Проверка подписки на канал (если настроен)
    if configuration.channel_id:
        try:
            member = await bot.get_chat_member(
                chat_id=configuration.channel_id,
                user_id=message.from_user.id
            )
            if member.status in ["left", "kicked"]:
                await message.answer(
                    f"⚠️ Вы вышли из нашего канала!\n\n"
                    f"Для продолжения использования бота, пожалуйста, вернитесь в канал:\n"
                    f"{configuration.channel_invite_link}\n\n"
                    f"После возврата снова нажмите /start",
                    parse_mode=types.ParseMode.HTML,
                )
                return
        except Exception as e:
            logger.error(f"Ошибка при проверке подписки в /start: {e}")
    
    if database.selector.is_exist_user(message.from_user.id):
        if database.selector.is_subscription_end(message.from_user.id):
            await message.answer(
                f"Привет, {message.from_user.full_name or message.from_user.username}, твоя подписка закончилась, оплати её, чтобы продолжить пользоваться VPN",
                reply_markup=await kb.free_user_kb(message.from_user.id),
            )
        else:
            await message.answer(
                f"Привет, {message.from_user.full_name or message.from_user.username}, твоя подписка действительна до {database.selector.get_subscription_end_date(message.from_user.id)}",
                reply_markup=await kb.payed_user_kb(),
            )
        return

    # Новый пользователь - проверяем, был ли использован триал
    trial_used = database.selector.is_trial_used(message.from_user.id)
    
    if not trial_used and configuration.channel_id:
        # Проверяем, состоит ли пользователь в канале
        try:
            member = await bot.get_chat_member(
                chat_id=configuration.channel_id,
                user_id=message.from_user.id
            )
            if member.status not in ["left", "kicked"]:
                # Пользователь в канале и не использовал триал - даем 3 дня
                await message.reply(
                    f"Привет, {message.from_user.full_name or message.from_user.username}!\n"
                    f"🎉 Ты получил 3 дня бесплатного триального периода!\n\n"
                    f"Чтобы начать пользоваться VPN, нажми кнопку '🆕 Создать конфиг'",
                    reply_markup=await kb.payed_user_kb(),
                )
                # Вставляем пользователя с триальным периодом 3 дня
                database.insert_new_user(message, trial_days=3)
                
                # notify admin about new user with trial
                for admin in configuration.admins:
                    await bot.send_message(
                        admin,
                        f"🎁 Новый пользователь с триалом: {hcode(message.from_user.full_name)}\n"
                        f"id: {hcode(message.from_user.id)}, username: {hcode(message.from_user.username)}\n"
                        f"Триальный период: 3 дня",
                        parse_mode=types.ParseMode.HTML,
                    )
                return
        except Exception as e:
            logger.error(f"Ошибка при проверке триала: {e}")
    
    # Если триал уже использован или канал не настроен
    await message.reply(
        f"Привет, {message.from_user.full_name or message.from_user.username}!\nЧтобы начать пользоваться VPN, оплати подписку",
        reply_markup=await kb.free_user_kb(message.from_user.id),
    )
    await bot.send_message(
        message.from_user.id,
        "Подробное описание бота и его функционала доступно на "
        f"{hlink('странице','https://telegra.ph/FAQ-po-botu-01-08')}, "
        "оплачивая подписку, вы соглашаетесь с правилами использования бота и условиями возврата средств, указанными в статье выше.",
        parse_mode=types.ParseMode.HTML,
    )
    database.insert_new_user(message, trial_days=0)

    # notify admin about new user
    for admin in configuration.admins:
        # format: Новый пользователь: Имя (id: id), username, id like code format in markdown
        await bot.send_message(
            admin,
            f"Новый пользователь: {hcode(message.from_user.full_name)}\n"
            f"id: {hcode(message.from_user.id)}, username: {hcode(message.from_user.username)}",
            parse_mode=types.ParseMode.HTML,
        )


@rate_limit(limit=5)
async def cmd_pay(message: types.Message, state: FSMContext) -> types.Message:
    # на данный момент нет возможности подключить платежную систему, поэтому временно отключено
    await NewPayment.payment_image.set()
    await bot.send_message(
        message.from_user.id,
        "В данный момент нет возможности совершить платеж в боте."
        f"Для оплаты подписки переведите {configuration.base_subscription_monthly_price_rubles}₽ на карту {hcode(configuration.payment_card)} "
        "и отправьте скриншот чека/операции в ответ на это сообщение.",
        parse_mode=types.ParseMode.HTML,
        reply_markup=await kb.cancel_payment_kb(),
    )


@rate_limit(limit=5)
async def got_payment_screenshot(message: types.Message, state: FSMContext):
    if message.content_type != "photo":
        await message.reply(
            "Пожалуйста, отправьте скриншот чека/операции в ответ на это сообщение."
        )
        return

    await message.reply("Подождите, пока мы проверим вашу оплату.")
    await state.finish()
    # forwards screenshot to admin
    for admin in configuration.admins:
        await message.forward(admin)
        give_help_command = f"/give {message.from_user.id} 30"
        await bot.send_message(
            admin,
            f"Пользователь {message.from_user.full_name}\n"
            f"id: {hcode(message.from_user.id)}, username: {hcode(message.from_user.username)} оплатил подписку на VPN.\n\n"
            "Проверьте оплату и активируйте VPN для пользователя.\n"
            f"{hcode(give_help_command)}",
            parse_mode=types.ParseMode.HTML,
        )


async def cancel_payment(query: types.CallbackQuery, state: FSMContext):
    await state.finish()
    await query.message.edit_text("Оплата отменена.", reply_markup=None)


# successful payment
async def successful_payment_handler(message: types.Message):
    database.update_user_payment(message.from_user.id)
    database.insert_new_payment(message)
    if database.selector.is_user_have_config(message.from_user.id):
        try:
            await vpn_config.reconnect_payed_user(message.from_user.id)
        except Exception as e:
            logger.error(e)

    await message.answer(
        f"{message.from_user.full_name or message.from_user.username}, твой доступ к VPN продлен до {database.selector.get_subscription_end_date(message.from_user.id)}",
        reply_markup=await kb.payed_user_kb(),
    )


async def cmd_my_configs(message: types.Message):
    if database.selector.all_user_configs(message.from_user.id):
        await message.answer(
            "Отображаю твои конфиги на кнопках",
            reply_markup=await kb.configs_kb(message.from_user.id),
        )
    else:
        await message.answer(
            "У тебя нет конфигов",
            reply_markup=await kb.configs_kb(message.from_user.id),
        )


async def cmd_menu(message: types.Message):
    if database.selector.is_subscription_end(message.from_user.id):
        await message.answer(
            "Возвращаю тебя в основное меню",
            reply_markup=await kb.free_user_kb(message.from_user.id),
        )
    else:
        await message.answer(
            "Возвращаю тебя в основное меню", reply_markup=await kb.payed_user_kb()
        )


@rate_limit(limit=5)
async def create_new_config(message: types.Message, state=FSMContext):
    # Check if user has reached max configs (10)
    config_count = database.selector.get_user_config_count(message.from_user.id)
    max_configs = 10
    
    if config_count >= max_configs:
        await message.answer(
            f"⚠️ Вы достигли максимального количества конфигов ({max_configs}).\n\n"
            f"Удалите старые конфиги или обратитесь к администратору для увеличения лимита.",
            reply_markup=await kb.configs_kb(message.from_user.id),
        )
        return
    
    # Calculate days per config after creating new one
    new_config_count = config_count + 1
    days_per_config = 30 // new_config_count
    
    await message.answer(
        f"⚠️ Внимание! Дни подписки распределяются между всеми конфигами.\n\n"
        f"У вас сейчас {config_count} конфиг(ов).\n"
        f"После создания нового конфига (всего будет {new_config_count}):\n"
        f"• Каждый конфиг получит по {days_per_config} дней\n"
        f"• Общий срок подписки останется 30 дней\n\n"
        f"Максимум можно создать {max_configs} конфигов (по 3 дня каждый).\n\n"
        f"Продолжить создание конфига?",
        reply_markup=await kb.confirm_new_config_kb(),
    )
    await NewConfig.waiting_confirmation.set()


async def device_selected(call: types.CallbackQuery, state=FSMContext):
    """
    This handler will be called when user presses config button
    """
    # Check for config limit reached callback
    if call.data == "config_limit_reached":
        await call.answer("⚠️ Вы достигли максимального количества конфигов (10)!", show_alert=True)
        return
    
    await state.update_data(device=call.data)
    # edit message text and delete keyboard from message
    await call.message.edit_text(
        f"Приступаю к созданию конфига", reply_markup=None
    )
    await state.finish()

    # add +1 to user config count
    database.update_user_config_count(call.from_user.id)

    # Get next config number for this user
    config_count = database.selector.get_user_config_count(call.from_user.id)
    config_number = config_count  # Use current count as the config number (1, 2, 3, etc.)
    
    device = f"CONFIG_{config_number}"
    user_config = await vpn_config.update_server_config(
        username=call.from_user.username, device=device
    )

    database.insert_new_config(
        user_id=call.from_user.id,
        username=call.from_user.username,
        device=device,
        config=user_config,
    )

    io_config_file = BytesIO(user_config.encode("utf-8"))
    filename = f"{call.from_user.username}_{config_number}.conf"

    # send config file
    await call.message.answer_document(
        types.InputFile(
            io_config_file,
            filename=filename,
        ),
        reply_markup=await kb.configs_kb(call.from_user.id),
    )

    # Always create QR code for all configs
    config_qr_code = create_qr_code_from_peer_data(user_config)
    await call.message.answer_photo(
        types.InputFile(
            config_qr_code,
            filename=f"{call.from_user.username}_{config_number}.png",
        ),
    )


async def cancel_config_creation(call: types.CallbackQuery, state=FSMContext):
    await state.finish()
    await call.message.edit_text("Отмена создания конфига", reply_markup=None)


async def confirm_new_config_handler(call: types.CallbackQuery, state=FSMContext):
    """Handler for confirming new config creation"""
    await call.message.edit_text(
        "Для какого устройства ты хочешь создать конфиг?",
        reply_markup=await kb.device_kb(call.from_user.id),
    )
    await NewConfig.device.set()


async def cancel_new_config_handler(call: types.CallbackQuery, state=FSMContext):
    """Handler for canceling new config creation"""
    await state.finish()
    await call.message.edit_text("Создание конфига отменено", reply_markup=None)


@rate_limit(limit=5)
async def cmd_show_config(message: types.Message, state=FSMContext):
    # Extract config number from message text (e.g., "CONFIG_1" -> 1)
    try:
        # Message text format: "CONFIG_1", "CONFIG_2", etc.
        config_number = int(message.text.split("_")[1])
    except (IndexError, ValueError):
        await message.answer("❌ Неверный формат конфига")
        return
    
    config_name = f"CONFIG_{config_number}"
    
    config = database.selector.get_user_config(
        user_id=message.from_user.id,
        config_name=config_name,
    )
    
    if not config:
        await message.answer("❌ Конфиг не найден")
        return
    
    filename = f"{message.from_user.username}_{config_number}.conf"
    io_config_file = BytesIO(config.encode("utf-8"))

    # send config file
    await message.answer_document(
        types.InputFile(
            io_config_file,
            filename=filename,
        ),
    )

    # Always create QR code for all configs
    config_qr_code = create_qr_code_from_peer_data(config)
    await message.answer_photo(
        types.InputFile(
            config_qr_code,
            filename=f"{message.from_user.username}_{config_number}.png",
        ),
    )


@rate_limit(limit=5)
async def cmd_support(message: types.Message):
    # send telegraph page with support info (link: https://telegra.ph/FAQ-po-botu-01-08)
    await message.answer(
        f"Подробное описание бота и его функционала доступно на {hlink('странице','https://telegra.ph/FAQ-po-botu-01-08')}",
        parse_mode=types.ParseMode.HTML,
    )

    admin_username = selector.get_username_by_id(configuration.admins[0])
    admin_telegram_link = f"t.me/{admin_username}"
    await message.answer(
        f"Если у тебя все еще остались вопросы, то ты можешь написать {hlink('мне',admin_telegram_link)} лично",
        parse_mode=types.ParseMode.HTML,
    )


@rate_limit(limit=5)
async def cmd_show_end_time(message: types.Message):
    # show user end time
    await message.answer(
        f"{message.from_user.full_name or message.from_user.username}, "
        f"твой доступ к VPN закончится {database.selector.get_subscription_end_date(message.from_user.id)}"
    )


@rate_limit(limit=2)
async def cmd_show_subscription(message: types.Message):
    await message.answer(
        f"{message.from_user.full_name or message.from_user.username}, "
        "здесь ты можешь распорядиться своей подпиской",
        reply_markup=await kb.subscription_management_kb(),
    )


@rate_limit(limit=5)
async def cmd_check_channel_subscription(message: types.Message):
    """Проверка подписки пользователя на канал"""
    from data import configuration
    
    if not configuration.channel_id:
        await message.answer("❌ Проверка подписки не настроена администратором.")
        return
    
    try:
        member = await bot.get_chat_member(
            chat_id=configuration.channel_id,
            user_id=message.from_user.id
        )
        
        if member.status in ["left", "kicked"]:
            await message.answer(
                f"⚠️ Вы не состоите в нашем канале!\\n\\n"
                f"Для продолжения использования бота, пожалуйста, подпишитесь:\\n"
                f"{configuration.channel_invite_link}\\n\\n"
                f"После подписки нажмите кнопку '✅ Проверить подписку' снова.",
                parse_mode=types.ParseMode.HTML,
            )
        else:
            await message.answer(
                "✅ Вы подписаны на наш канал! Спасибо!",
                reply_markup=await kb.free_user_kb(message.from_user.id) 
                if database.selector.is_subscription_end(message.from_user.id)
                else await kb.payed_user_kb(message.from_user.id)
            )
    except Exception as e:
        logger.error(f"Ошибка при проверке подписки: {e}")
        await message.answer("⚠️ Произошла ошибка при проверке подписки. Попробуйте позже.")


@rate_limit(limit=30)
async def cmd_refresh_status(message: types.Message):
    """Обновление статуса подписки пользователя"""
    from data import configuration
    
    # Проверка подписки на канал (если настроен)
    if configuration.channel_id:
        try:
            member = await bot.get_chat_member(
                chat_id=configuration.channel_id,
                user_id=message.from_user.id
            )
            if member.status in ["left", "kicked"]:
                await message.answer(
                    f"⚠️ Вы вышли из нашего канала!\\n\\n"
                    f"Для продолжения использования бота, пожалуйста, вернитесь в канал:\\n"
                    f"{configuration.channel_invite_link}\\n\\n"
                    f"После возврата снова нажмите /start",
                    parse_mode=types.ParseMode.HTML,
                )
                return
        except Exception as e:
            logger.error(f"Ошибка при проверке подписки: {e}")
    
    # Обновляем информацию о подписке
    if database.selector.is_subscription_end(message.from_user.id):
        await message.answer(
            f"Привет, {message.from_user.full_name or message.from_user.username}!\\n"
            f"Твоя подписка закончилась {database.selector.get_subscription_end_date(message.from_user.id)}.\\n"
            f"Оплати подписку, чтобы продолжить пользоваться VPN.",
            parse_mode=types.ParseMode.HTML,
            reply_markup=await kb.free_user_kb(message.from_user.id),
        )
    else:
        await message.answer(
            f"Привет, {message.from_user.full_name or message.from_user.username}!\\n"
            f"Твоя подписка действительна до {database.selector.get_subscription_end_date(message.from_user.id)}.\\n"
            f"Пользуйся VPN с удовольствием!",
            parse_mode=types.ParseMode.HTML,
            reply_markup=await kb.payed_user_kb(message.from_user.id),
        )


@rate_limit(limit=3600)
async def cmd_reboot_wg_service(message: types.Message):
    await message.answer("Перезагрузка сервиса WireGuard...")
    vpn_config.restart_service()
    await message.answer("Сервис WireGuard перезагружен")
