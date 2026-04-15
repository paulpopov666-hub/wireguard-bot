from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from database import selector as select


async def device_kb(user_id: int):
    """returns inline keyboard with various options of cfg choosing"""
    existing_devices = [
        item[0].split("_")[-1] for item in select.all_user_configs(user_id=user_id)
    ]

    buttons = []
    if "iOS" not in existing_devices:
        buttons.append(InlineKeyboardButton(text="🍎 iOS", callback_data="ios_config_create_request"))
    if "ANDROID" not in existing_devices:
        buttons.append(InlineKeyboardButton(text="🤖 Android", callback_data="android_config_create_request"))
    
    buttons.append(InlineKeyboardButton(text="❌Отмена❌", callback_data="cancel_config_creation"))
    
    keyboard = [buttons[i:i+2] for i in range(0, len(buttons), 2)]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


async def cancel_payment_kb():
    """returns inline keyboard with cancel payment button"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="❌Отмена❌", callback_data="cancel_payment")]
    ])


# Админские клавиатуры
async def admin_main_kb():
    """Главное меню администратора"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📊 Статистика", callback_data="admin_stats"),
         InlineKeyboardButton(text="📢 Рассылка", callback_data="admin_broadcast")],
        [InlineKeyboardButton(text="🎫 Тикеты", callback_data="admin_tickets")],
        [InlineKeyboardButton(text="🔙 В главное меню", callback_data="user_main_menu")]
    ])


async def admin_stats_kb():
    """Клавиатура статистики"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔄 Обновить", callback_data="stats_refresh"),
         InlineKeyboardButton(text="📤 Экспорт", callback_data="stats_export")],
        [InlineKeyboardButton(text="🔙 Назад", callback_data="admin_main_menu")]
    ])


async def admin_broadcast_kb():
    """Клавиатура рассылки"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📣 Всем пользователям", callback_data="broadcast_all"),
         InlineKeyboardButton(text="⏰ Скоро окончание", callback_data="broadcast_expiring")],
        [InlineKeyboardButton(text="🔙 Назад", callback_data="admin_main_menu")]
    ])


async def admin_tickets_kb(ticket_id: int):
    """Клавиатура для работы с тикетом"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✏️ Ответить", callback_data=f"ticket_reply_{ticket_id}"),
         InlineKeyboardButton(text="✅ Закрыть", callback_data=f"ticket_close_{ticket_id}")],
        [InlineKeyboardButton(text="🔙 К списку", callback_data="admin_tickets_list")]
    ])


# Пользовательские клавиатуры
async def user_main_kb():
    """Главное меню пользователя"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔑 Мой VPN", callback_data="user_my_vpn"),
         InlineKeyboardButton(text="💳 Оплата", callback_data="user_payment")],
        [InlineKeyboardButton(text="👥 Рефералы", callback_data="user_referrals")],
        [InlineKeyboardButton(text="🆘 Поддержка", callback_data="user_support"),
         InlineKeyboardButton(text="📲 Приложения", callback_data="user_apps")]
    ])


async def payment_method_kb():
    """Payment method - only manual screenshot"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📸 Отправить скриншот оплаты", callback_data="pay_screenshot")],
        [InlineKeyboardButton(text="🔙 Назад", callback_data="user_main_menu")]
    ])


async def support_ticket_kb():
    """Клавиатура поддержки"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✏️ Создать тикет", callback_data="support_create")],
        [InlineKeyboardButton(text="📋 Мои тикеты", callback_data="support_list")],
        [InlineKeyboardButton(text="🔙 Назад", callback_data="user_main_menu")]
    ])


async def apps_kb():
    """Клавиатура приложений"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🍎 iOS (App Store)", url="https://apps.apple.com/ru/app/amneziawg/id6478942365")],
        [InlineKeyboardButton(text="🤖 Android (Play Market)", url="https://play.google.com/store/apps/details?id=org.amnezia.awg&hl=ru")],
        [InlineKeyboardButton(text="🔙 Назад", callback_data="user_main_menu")]
    ])


if __name__ == "__main__":
    ...
