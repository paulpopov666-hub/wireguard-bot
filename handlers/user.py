from loguru import logger
from os import remove
from io import BytesIO
from aiogram import types
from aiogram.fsm.context import FSMContext
from aiogram.utils.markdown import hcode, hlink

from middlewares import rate_limit
import keyboards as kb

import database
from loader import bot
from data import configuration
from loader import vpn_config
from database import selector, update, insert

from utils.fsm import NewConfig, NewPayment
from utils.qr_code import create_qr_code_from_peer_data


@rate_limit(limit=5)
async def cmd_start(message: types.Message) -> types.Message:
    if not message.from_user.username:
        await message.answer(
            f"Привет, {message.from_user.full_name}!\nУ тебя не установлен username, установи его в настройках телеграма и напиши /start\n",
            parse_mode=types.ParseMode.HTML,
        )
        return
    
    # Extract referrer from deep link (start parameter)
    referred_by = None
    if message.text and message.text.startswith("/start "):
        try:
            referrer_id = int(message.text.split()[1])
            if referrer_id != message.from_user.id:  # Can't refer yourself
                referred_by = referrer_id
        except (ValueError, IndexError):
            pass
    
    # Check if user exists in database
    if database.selector.is_exist_user(message.from_user.id):
        # User exists - check subscription status
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

    # New user - insert into database and handle trial/subscription
    database.insert_new_user(message, referred_by=referred_by)
    
    # Check required group membership if configured
    if configuration.required_group_id:
        is_member = await check_group_membership(message.from_user.id)
        if not is_member:
            await message.answer(
                f"Привет, {message.from_user.full_name or message.from_user.username}!\n"
                f"Для использования бота необходимо подписаться на нашу группу.\n"
                f"Нажмите кнопку ниже, чтобы вступить.",
                reply_markup=await kb.group_required_kb(configuration.required_group_id),
            )
            return
    
    # Give trial subscription to new user (1 day)
    update.set_trial_used(message.from_user.id)
    update.set_user_enddate_to_n(message.from_user.id, configuration.trial_days)
    
    await message.answer(
        f"Привет, {message.from_user.full_name or message.from_user.username}!\n"
        f"🎉 Вам активирован бесплатный пробный период на {configuration.trial_days} день!\n"
        f"Ваша подписка действительна до {database.selector.get_subscription_end_date(message.from_user.id)}",
        reply_markup=await kb.payed_user_kb(),
    )
    
    # Notify admins about new user with trial
    for admin in configuration.admins:
        user_mention = hlink(message.from_user.full_name or message.from_user.username, f"tg://user?id={message.from_user.id}")
        referral_info = f"\nПригласил: {hcode(referred_by)}" if referred_by else ""
        await bot.send_message(
            admin,
            f"🆕 Новый пользователь получил триал:\n"
            f"{user_mention}\n"
            f"id: {hcode(message.from_user.id)}\n"
            f"username: {hcode(message.from_user.username)}\n"
            f"Триальный период: {configuration.trial_days} дн.{referral_info}",
            parse_mode=types.ParseMode.HTML,
        )


async def check_group_membership(user_id: int) -> bool:
    """Check if user is a member of the required Telegram group"""
    try:
        member = await bot.get_chat_member(configuration.required_group_id, user_id)
        return member.status in ['member', 'administrator', 'creator']
    except Exception as e:
        logger.error(f"Failed to check group membership for user {user_id}: {e}")
        return False


@rate_limit(limit=5)
async def handle_joined_group(message: types.Message):
    """Handler for when user clicks 'I joined the group' button"""
    if not configuration.required_group_id:
        await message.answer("Проверка подписки на группу не настроена.")
        return
    
    is_member = await check_group_membership(message.from_user.id)
    if is_member:
        # Give trial subscription
        update.set_trial_used(message.from_user.id)
        update.set_user_enddate_to_n(message.from_user.id, configuration.trial_days)
        
        await message.answer(
            f"🎉 Спасибо! Вам активирован бесплатный пробный период на {configuration.trial_days} день!\n"
            f"Ваша подписка действительна до {database.selector.get_subscription_end_date(message.from_user.id)}",
            reply_markup=await kb.payed_user_kb(),
        )
        
        # Notify admins
        for admin in configuration.admins:
            user_mention = hlink(message.from_user.full_name or message.from_user.username, f"tg://user?id={message.from_user.id}")
            await bot.send_message(
                admin,
                f"🆕 Новый пользователь получил триал:\n"
                f"{user_mention}\n"
                f"id: {hcode(message.from_user.id)}\n"
                f"username: {hcode(message.from_user.username)}\n"
                f"Триальный период: {configuration.trial_days} дн.",
                parse_mode=types.ParseMode.HTML,
            )
    else:
        await message.answer(
            "❌ Вы ещё не вступили в группу. Пожалуйста, подпишитесь и нажмите кнопку снова.",
            reply_markup=await kb.group_required_kb(configuration.required_group_id),
        )


@rate_limit(limit=5)
async def cmd_pay(message: types.Message, state: FSMContext) -> types.Message:
    # на данный момент нет возможности подключить платежную систему, поэтому временно отключено
    await NewPayment.payment_image.set()
    await bot.send_message(
        message.from_user.id,
        "В данный момент нет возможности совершить платеж в боте. "
        f"Для оплаты подписки переведите {configuration.base_subscription_monthly_price_rubles}₽ на карту {hcode(configuration.payment_card)} "
        "и отправьте скриншот чека/операции в ответ на это сообщение.\n\n"
        "🎁 Реферальная программа:\n"
        "Пригласите друга и получите по 10 дней бонуса к подписке каждый раз, когда он оплатит услуги VPN!\n"
        "Ваша реферальная ссылка: https://t.me/{bot_username}?start={user_id}".format(
            bot_username=(await bot.get_me()).username,
            user_id=message.from_user.id
        ),
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
        
        # Check if user has a referrer and notify about potential bonus
        referrer_id = database.update.get_referrer_user_id(message.from_user.id)
        referral_note = ""
        if referrer_id:
            referral_note = f"\n\n🎁 Пользователь был приглашен пользователем с id: {hcode(referrer_id)}\n" \
                           f"После подтверждения оплаты начислите бонус 10 дней обоим:\n" \
                           f"{hcode('/give ' + str(message.from_user.id) + ' 10')} - приглашенному\n" \
                           f"{hcode('/give ' + str(referrer_id) + ' 10')} - пригласившему"
        
        await bot.send_message(
            admin,
            f"Пользователь {message.from_user.full_name}\n"
            f"id: {hcode(message.from_user.id)}, username: {hcode(message.from_user.username)} оплатил подписку на VPN.\n\n"
            "Проверьте оплату и активируйте VPN для пользователя.\n"
            f"{hcode(give_help_command)}{referral_note}",
            parse_mode=types.ParseMode.HTML,
        )


async def cancel_payment(query: types.CallbackQuery, state: FSMContext):
    await state.finish()
    await query.message.edit_text("Оплата отменена.", reply_markup=None)


# successful payment
async def successful_payment_handler(message: types.Message):
    database.update_user_payment(message.from_user.id)
    database.insert_new_payment(message)
    
    # Check if user has a referrer and award bonus days (10 days each)
    referrer_id = database.update.get_referrer_user_id(message.from_user.id)
    if referrer_id:
        # Award 10 days to the new user
        database.update.add_referral_bonus_days(message.from_user.id, 10)
        # Award 10 days to the referrer
        database.update.add_referral_bonus_days(referrer_id, 10)
        
        # Notify both users about the bonus
        for admin in configuration.admins:
            await bot.send_message(
                admin,
                f"🎁 Реферальный бонус начислен!\n"
                f"Пользователь {hcode(message.from_user.id)} оплатил подписку.\n"
                f"+10 дней бонуса пользователю {hcode(message.from_user.id)}\n"
                f"+10 дней бонуса пригласившему {hcode(referrer_id)}",
                parse_mode=types.ParseMode.HTML,
            )
    
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
            "Отображаем ваши конфиги на кнопках",
            reply_markup=await kb.configs_kb(message.from_user.id),
        )
    else:
        await message.answer(
            "У вас нет конфигов",
            reply_markup=await kb.configs_kb(message.from_user.id),
        )


async def cmd_menu(message: types.Message):
    if database.selector.is_subscription_end(message.from_user.id):
        await message.answer(
            "Возвращаем вас в основное меню",
            reply_markup=await kb.free_user_kb(message.from_user.id),
        )
    else:
        await message.answer(
            "Возвращаем вас в основное меню", reply_markup=await kb.payed_user_kb()
        )


@rate_limit(limit=5)
async def create_new_config(message: types.Message, state=FSMContext):
    await message.answer(
        "Для какого устройства вы хотите создать конфиг?",
        reply_markup=await kb.device_kb(message.from_user.id),
    )
    await NewConfig.device.set()


async def device_selected(call: types.CallbackQuery, state=FSMContext):
    """
    This handler will be called when user presses iOS or Android button
    """
    await state.update_data(device=call.data)
    # edit message text and delete keyboard from message
    device_name = "🍎 iOS" if call.data.startswith("ios") else "🤖 Android"
    await call.message.edit_text(
        f"Вы выбрали {device_name}, приступаем к созданию конфига", reply_markup=None
    )
    await state.finish()

    # add +1 to user config count
    database.update_user_config_count(call.from_user.id)

    device = "iOS" if call.data.startswith("ios") else "ANDROID"
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
    filename = f"{configuration.configs_prefix}_{call.from_user.username}_{device}.conf"

    # send config file
    await call.message.answer_document(
        types.InputFile(
            io_config_file,
            filename=filename,
        ),
        reply_markup=await kb.configs_kb(call.from_user.id),
    )

    # QR code for both mobile platforms
    config_qr_code = create_qr_code_from_peer_data(user_config)
    await call.message.answer_photo(
        types.InputFile(
            config_qr_code,
            filename=f"{configuration.configs_prefix}_{call.from_user.username}.png",
        ),
    )


async def cancel_config_creation(call: types.CallbackQuery, state=FSMContext):
    await state.finish()
    await call.message.edit_text("Отмена создания конфига", reply_markup=None)


@rate_limit(limit=5)
async def cmd_show_config(message: types.Message, state=FSMContext):
    if message.text.lower().endswith("ios"):
        device = "iOS"
    elif message.text.lower().endswith("android"):
        device = "ANDROID"
    else:
        await message.answer("Неизвестное устройство. Выберите конфиг из меню.")
        return

    config = database.selector.get_user_config(
        user_id=message.from_user.id,
        config_name=f"{message.from_user.username}_{device}",
    )
    filename = (
        f"{configuration.configs_prefix}_{message.from_user.username}_{device}.conf"
    )
    io_config_file = BytesIO(config.encode("utf-8"))

    # send config file
    await message.answer_document(
        types.InputFile(
            io_config_file,
            filename=filename,
        ),
    )

    # QR code for both mobile platforms
    image_filename = (
        f"{configuration.configs_prefix}_{message.from_user.username}.png"
    )
    config_qr_code = create_qr_code_from_peer_data(config)

    await message.answer_photo(
        types.InputFile(
            config_qr_code,
            filename=image_filename,
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
        f"Если у вас все еще остались вопросы, то вы можете написать {hlink('нам',admin_telegram_link)} лично",
        parse_mode=types.ParseMode.HTML,
    )


@rate_limit(limit=5)
async def cmd_show_end_time(message: types.Message):
    # show user end time
    await message.answer(
        f"{message.from_user.full_name or message.from_user.username}, "
        f"ваш доступ к VPN закончится {database.selector.get_subscription_end_date(message.from_user.id)}"
    )


@rate_limit(limit=2)
async def cmd_show_subscription(message: types.Message):
    await message.answer(
        f"{message.from_user.full_name or message.from_user.username}, "
        "здесь вы можете распорядиться своей подпиской",
        reply_markup=await kb.subscription_management_kb(),
    )


@rate_limit(limit=3600)
async def cmd_reboot_wg_service(message: types.Message):
    await message.answer("Перезагрузка сервиса WireGuard...")
    vpn_config.restart_service()
    await message.answer("Сервис WireGuard перезагружен")
