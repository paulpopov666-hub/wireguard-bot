from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from database.selector import is_user_have_config, all_user_configs, get_subscription_end_date
from datetime import datetime, timedelta
import database


async def payed_user_kb():
    keyboard = ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    keyboard.insert(KeyboardButton("📁 Мои конфиги"))
    keyboard.insert(KeyboardButton("🕑 Моя подписка"))
    keyboard.insert(KeyboardButton("📝 Помощь"))
    keyboard.insert(KeyboardButton("☢️Перезагрузить VPN"))
    return keyboard


async def free_user_kb(user_id: int):
    keyboard = ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    keyboard.insert(KeyboardButton("💵 Оплатить"))
    keyboard.insert(KeyboardButton("👥 Пригласить друга"))
    if is_user_have_config(user_id=user_id):
        keyboard.insert(KeyboardButton("📁 Мои конфиги"))
    return keyboard


async def group_required_kb(group_id: int):
    """Returns keyboard with button to join required group"""
    keyboard = ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    keyboard.insert(KeyboardButton("✅ Я вступил в группу"))
    return keyboard


async def configs_kb(user_id: int):
    configs_kb = ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    configs = all_user_configs(user_id=user_id)

    if configs:
        for config in configs:
            device_name = "Android" if config[0].split('_')[-1] == 'PHONE' else "iOS"
            configs_kb.insert(
                KeyboardButton(
                    f"🔐 {device_name}"
                )
            )

    # Allow purchasing additional configs (50% of base price)
    configs_kb.insert(KeyboardButton("➕ Купить доп. конфиг"))
    configs_kb.insert(KeyboardButton("🔙 Назад"))

    return configs_kb


async def subscription_management_kb():
    keyboard = ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    keyboard.insert(KeyboardButton("📅 Дата отключения"))
    keyboard.insert(KeyboardButton("💵 Продлить"))
    keyboard.insert(KeyboardButton("👥 Реферальная программа"))
    keyboard.insert(KeyboardButton("🔙 Назад"))
    return keyboard


async def payment_info_kb() -> InlineKeyboardMarkup:
    """Keyboard with payment information and warnings"""
    kb = InlineKeyboardMarkup(row_width=1)
    kb.add(InlineKeyboardButton("💳 Оплатить картой", callback_data="pay_card"))
    kb.add(InlineKeyboardButton("🔙 Отмена", callback_data="cancel_payment"))
    return kb


async def referral_menu_kb(bot_username: str, user_id: int) -> InlineKeyboardMarkup:
    """Referral program menu with link and info"""
    kb = InlineKeyboardMarkup(row_width=1)
    referral_link = f"https://t.me/{bot_username}?start={user_id}"
    
    kb.add(InlineKeyboardButton(
        "📋 Скопировать ссылку", 
        url=f"tg://resolve?domain={bot_username}&start={user_id}"
    ))
    kb.add(InlineKeyboardButton("🔙 Назад", callback_data="back_to_main"))
    return kb


async def buy_additional_config_kb(price: int) -> InlineKeyboardMarkup:
    """Keyboard for purchasing additional config"""
    kb = InlineKeyboardMarkup(row_width=1)
    kb.add(InlineKeyboardButton(
        f"💰 Купить за {price}₽ (50% от цены)", 
        callback_data="buy_additional_config"
    ))
    kb.add(InlineKeyboardButton("❌ Отмена", callback_data="cancel_config_purchase"))
    return kb


async def admin_main_kb() -> ReplyKeyboardMarkup:
    """Main admin panel keyboard with all commands as buttons"""
    keyboard = ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    keyboard.insert(KeyboardButton("📊 Статистика"))
    keyboard.insert(KeyboardButton("👥 Пользователи"))
    keyboard.insert(KeyboardButton("⏰ Продлить подписку"))
    keyboard.insert(KeyboardButton("🔄 Перезапустить WG"))
    keyboard.insert(KeyboardButton("⚙️ Настройки обфускации"))
    keyboard.insert(KeyboardButton("📨 Рассылка"))
    keyboard.insert(KeyboardButton("🎫 Тикеты поддержки"))
    keyboard.insert(KeyboardButton("🔙 В меню"))
    return keyboard


async def admin_stats_kb() -> InlineKeyboardMarkup:
    """Keyboard for statistics filters"""
    kb = InlineKeyboardMarkup(row_width=3)
    kb.add(InlineKeyboardButton("Все", callback_data="stats_all"))
    kb.add(InlineKeyboardButton("Активные", callback_data="stats_active"))
    kb.add(InlineKeyboardButton("Истекшие", callback_data="stats_inactive"))
    kb.add(InlineKeyboardButton("🔙 Назад", callback_data="admin_back"))
    return kb


async def admin_extend_kb() -> InlineKeyboardMarkup:
    """Keyboard for extending subscription"""
    kb = InlineKeyboardMarkup(row_width=3)
    for days in [7, 14, 30, 60, 90, 365]:
        kb.add(InlineKeyboardButton(f"+{days} дн.", callback_data=f"extend_{days}"))
    kb.add(InlineKeyboardButton("🔙 Отмена", callback_data="admin_back"))
    return kb


async def admin_obfuscation_kb() -> InlineKeyboardMarkup:
    """Keyboard for obfuscation settings"""
    kb = InlineKeyboardMarkup(row_width=2)
    kb.add(InlineKeyboardButton("Jc", callback_data="obf_jc"))
    kb.add(InlineKeyboardButton("Jmin", callback_data="obf_jmin"))
    kb.add(InlineKeyboardButton("Jmax", callback_data="obf_jmax"))
    kb.add(InlineKeyboardButton("S1", callback_data="obf_s1"))
    kb.add(InlineKeyboardButton("S2", callback_data="obf_s2"))
    kb.add(InlineKeyboardButton("H1-H4", callback_data="obf_h"))
    kb.add(InlineKeyboardButton("🔙 Назад", callback_data="admin_back"))
    return kb


async def support_ticket_kb() -> InlineKeyboardMarkup:
    """Keyboard for support ticket system"""
    kb = InlineKeyboardMarkup(row_width=2)
    kb.add(InlineKeyboardButton("✉️ Создать тикет", callback_data="create_ticket"))
    kb.add(InlineKeyboardButton("📋 Мои тикеты", callback_data="my_tickets"))
    kb.add(InlineKeyboardButton("🔙 Назад", callback_data="back_to_main"))
    return kb
