"""
Simple admin handlers for Amnezia WireGuard VPN Bot
- Statistics dashboard
- Broadcast system
- Support ticket system
"""
from aiogram import types, Dispatcher
from aiogram.fsm.context import FSMContext
from aiogram.utils.markdown import hcode, hbold, hlink
from loguru import logger
import database
from loader import bot, vpn_config
from data import configuration
from utils.fsm import AdminBroadcast
from keyboards.inline import (
    admin_stats_kb, 
    admin_broadcast_kb,
    support_ticket_kb
)
import asyncio
from datetime import datetime, timedelta


async def cmd_stats(message: types.Message):
    """Display comprehensive statistics"""
    if message.from_user.id not in configuration.admins:
        return
    
    # Calculate statistics
    total_users = database.selector.count_all_users()
    active_users = database.selector.count_active_users()
    trial_users = database.selector.count_trial_users()
    
    # Revenue stats (last 30 days)
    payments = database.selector.get_payments_last_days(30)
    total_revenue = sum(p.amount for p in payments) if payments else 0
    
    # Conversion rate
    converted_users = database.selector.count_converted_from_trial()
    conversion_rate = (converted_users / total_users * 100) if total_users > 0 else 0
    
    # Configs count
    total_configs = database.selector.count_all_configs()
    
    stats_text = (
        f"{hbold('📊 Статистика сервиса VPN')}\n\n"
        f"{hbold('👥 Пользователи:')}\n"
        f"• Всего: {total_users}\n"
        f"• Активные: {active_users}\n"
        f"• Триал: {trial_users}\n\n"
        f"{hbold('💰 Финансы (30 дней):')}\n"
        f"• Выручка: {total_revenue}₽\n"
        f"• Платежей: {len(payments)}\n\n"
        f"{hbold('📈 Конверсия:')}\n"
        f"• Из триала в оплату: {converted_users}\n"
        f"• Конверсия: {conversion_rate:.1f}%\n\n"
        f"{hbold('🔧 Конфигурации:')}\n"
        f"• Всего выдано: {total_configs}\n"
        f"• Среднее на пользователя: {total_configs / total_users:.1f if total_users > 0 else 0}\n"
    )
    
    await message.answer(stats_text, reply_markup=await admin_stats_kb())


async def cmd_broadcast(message: types.Message):
    """Start broadcast message creation"""
    if message.from_user.id not in configuration.admins:
        return
    
    await message.answer(
        f"{hbold('📢 Создание рассылки')}\n\n"
        f"Выберите аудиторию:",
        reply_markup=await admin_broadcast_kb()
    )


async def select_broadcast_audience(call: types.CallbackQuery):
    """Select audience for broadcast"""
    audience = call.data.split('_')[1]
    await AdminBroadcast.message.set()
    await call.message.edit_text(
        f"Введите текст рассылки для аудитории: {audience}\n"
        f"Поддерживается HTML и кнопки."
    )


async def send_broadcast(message: types.Message, state: FSMContext):
    """Send broadcast to selected audience"""
    async with state.proxy() as data:
        audience = data.get('audience', 'all')
    
    # Get target users based on audience
    if audience == 'all':
        users = database.selector.get_all_user_ids()
    elif audience == 'trial':
        users = database.selector.get_trial_user_ids()
    elif audience == 'expiring_soon':
        users = database.selector.get_expiring_soon_ids(days=3)
    else:
        users = []
    
    sent_count = 0
    failed_count = 0
    
    progress_msg = await message.answer(f"📢 Начало рассылки... 0/{len(users)}")
    
    for user_id in users:
        try:
            await bot.send_message(user_id, message.text, parse_mode="HTML")
            sent_count += 1
        except Exception as e:
            logger.error(f"Failed to send to {user_id}: {e}")
            failed_count += 1
        
        # Update progress every 10 messages
        if sent_count % 10 == 0:
            await progress_msg.edit_text(f"📢 Отправлено: {sent_count}/{len(users)}")
            await asyncio.sleep(0.5)  # Avoid rate limits
    
    await progress_msg.edit_text(
        f"✅ Рассылка завершена!\n"
        f"Отправлено: {sent_count}\n"
        f"Не доставлено: {failed_count}"
    )
    await state.finish()


async def cmd_support_tickets(message: types.Message):
    """Show support tickets interface"""
    if message.from_user.id not in configuration.admins:
        return
    
    tickets = database.selector.get_open_tickets()
    
    if not tickets:
        await message.answer("🎫 Нет открытых обращений в поддержку")
        return
    
    for ticket in tickets:
        await message.answer(
            f"🎫 Обращение #{ticket['id']}\n"
            f"Пользователь: {hlink(ticket['username'], f'tg://user?id={ticket['user_id']}')}\n"
            f"Дата: {ticket['created_at']}\n"
            f"Сообщение: {ticket['message']}",
            reply_markup=await support_ticket_kb(ticket['id'])
        )


async def handle_support_request(message: types.Message):
    """User creates support ticket"""
    # Save ticket to database
    database.insert.insert_support_ticket(
        user_id=message.from_user.id,
        username=message.from_user.username,
        message=message.text
    )
    
    await message.answer(
        "✅ Ваше обращение принято в работу.\n"
        "Администратор ответит вам в ближайшее время."
    )
    
    # Notify admins
    for admin in configuration.admins:
        await bot.send_message(
            admin,
            f"🎫 Новое обращение в поддержку\n"
            f"От: {hlink(message.from_user.full_name, f'tg://user?id={message.from_user.id}')}\n"
            f"Сообщение: {message.text}",
            reply_markup=await support_ticket_kb(None)
        )


def setup(dp: Dispatcher):
    """Register handlers"""
    # Statistics
    dp.register_message_handler(cmd_stats, commands=['stats'])
    
    # Broadcast
    dp.register_message_handler(cmd_broadcast, commands=['broadcast'])
    dp.register_callback_query_handler(select_broadcast_audience, text_startswith='broadcast_')
    dp.register_message_handler(send_broadcast, state=AdminBroadcast.message)
    
    # Support tickets
    dp.register_message_handler(handle_support_request, commands=['support'])
    dp.register_message_handler(cmd_support_tickets, commands=['tickets'])
