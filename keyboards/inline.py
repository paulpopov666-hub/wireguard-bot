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
        [InlineKeyboardButton(text="⚙️ Настройки обфускации", callback_data="admin_obfuscation"),
         InlineKeyboardButton(text="🎫 Тикеты", callback_data="admin_tickets")],
        [InlineKeyboardButton(text="🎁 Промокоды", callback_data="admin_promo"),
         InlineKeyboardButton(text="🔧 Тех. работы", callback_data="admin_maintenance")],
        [InlineKeyboardButton(text="👥 Пользователи", callback_data="admin_users"),
         InlineKeyboardButton(text="🔙 В главное меню", callback_data="user_main_menu")]
    ])


async def admin_stats_kb():
    """Клавиатура статистики"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔄 Обновить", callback_data="stats_refresh"),
         InlineKeyboardButton(text="📤 Экспорт", callback_data="stats_export")],
        [InlineKeyboardButton(text="🔙 Назад", callback_data="admin_main_menu")]
    ])


async def admin_obfuscation_kb():
    """Клавиатура настройки обфускации"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔄 Сгенерировать новые параметры", callback_data="obf_generate_new")],
        [InlineKeyboardButton(text="📝 Ввести вручную", callback_data="obf_enter_manual")],
        [InlineKeyboardButton(text="🔙 Назад", callback_data="admin_main_menu")]
    ])


async def admin_broadcast_kb():
    """Клавиатура рассылки"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📣 Всем пользователям", callback_data="broadcast_all"),
         InlineKeyboardButton(text="⏰ Скоро окончание", callback_data="broadcast_expiring")],
        [InlineKeyboardButton(text="💰 Оплатившие", callback_data="broadcast_paid"),
         InlineKeyboardButton(text="🆕 Триал пользователи", callback_data="broadcast_trial")],
        [InlineKeyboardButton(text="🔙 Назад", callback_data="admin_main_menu")]
    ])


async def admin_tickets_kb(ticket_id: int):
    """Клавиатура для работы с тикетом"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✏️ Ответить", callback_data=f"ticket_reply_{ticket_id}"),
         InlineKeyboardButton(text="✅ Закрыть", callback_data=f"ticket_close_{ticket_id}")],
        [InlineKeyboardButton(text="🔙 К списку", callback_data="admin_tickets_list")]
    ])


async def admin_promo_kb():
    """Клавиатура промокодов"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="➕ Создать промокод", callback_data="promo_create"),
         InlineKeyboardButton(text="📋 Список активных", callback_data="promo_list")],
        [InlineKeyboardButton(text="🔙 Назад", callback_data="admin_main_menu")]
    ])


async def maintenance_mode_kb(is_active: bool):
    """Клавиатура режима тех. работ"""
    action = "Отключить" if is_active else "Включить"
    status = "🟢 ВКЛЮЧЕНО" if is_active else "🔴 ВЫКЛЮЧЕНО"
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=f"{action} режим тех. работ ({status})", callback_data="toggle_maintenance")],
        [InlineKeyboardButton(text="🔙 Назад", callback_data="admin_main_menu")]
    ])


# Пользовательские клавиатуры
async def user_main_kb():
    """Главное меню пользователя"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔑 Мой VPN", callback_data="user_my_vpn"),
         InlineKeyboardButton(text="💳 Оплата", callback_data="user_payment")],
        [InlineKeyboardButton(text="👥 Рефералы", callback_data="user_referrals"),
         InlineKeyboardButton(text="🎁 Промокод", callback_data="user_promo")],
        [InlineKeyboardButton(text="🆘 Поддержка", callback_data="user_support"),
         InlineKeyboardButton(text="📲 Приложения", callback_data="user_apps")]
    ])


async def payment_method_kb():
    """Выбор метода оплаты"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📸 Скриншот платежа", callback_data="pay_screenshot")],
        [InlineKeyboardButton(text="🪙 CryptoBot", callback_data="pay_cryptobot")],
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
