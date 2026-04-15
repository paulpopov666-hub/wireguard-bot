from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from database.selector import is_user_have_config, all_user_configs


async def payed_user_kb(user_id: int = None):
    keyboard = ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    keyboard.insert(KeyboardButton("📁 Мои конфиги"))
    keyboard.insert(KeyboardButton("🕑 Моя подписка"))
    keyboard.insert(KeyboardButton("📝 Помощь"))
    
    # Добавляем кнопку перезагрузки VPN только если это не админ
    # Админы имеют отдельную кнопку в меню
    from data import configuration
    if user_id not in configuration.admins:
        keyboard.insert(KeyboardButton("♻️ Обновить статус"))
    
    return keyboard


async def free_user_kb(user_id: int):
    keyboard = ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    keyboard.insert(
        KeyboardButton(
            "💵 Оплатить",
        )
    )
    if is_user_have_config(user_id=user_id):
        keyboard.insert(KeyboardButton("📁 Мои конфиги"))
    
    # Добавляем кнопку проверки подписки на канал
    from data import configuration
    if configuration.channel_id:
        keyboard.insert(KeyboardButton("✅ Проверить подписку"))
    
    return keyboard


async def configs_kb(user_id: int):
    configs_kb = ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    configs = all_user_configs(user_id=user_id)
    
    # Get config count to show in button
    from database.selector import get_user_config_count
    config_count = get_user_config_count(user_id=user_id)
    max_configs = 10

    if configs:
        for config in configs:
            # Extract config number from config name (e.g., "CONFIG_1" -> 1)
            config_name = config[0]
            try:
                config_num = config_name.split("_")[-1]
                configs_kb.insert(
                    KeyboardButton(f"🔐 Конфиг #{config_num}")
                )
            except (IndexError, ValueError):
                configs_kb.insert(
                    KeyboardButton(f"🔐 {config_name}")
                )

    # Show create button only if user has less than max configs
    if not configs or len(configs) < max_configs:
        configs_kb.insert(KeyboardButton(f"🆕 Создать конфиг ({config_count}/{max_configs})"))

    configs_kb.insert(KeyboardButton("🔙 Назад"))

    return configs_kb


async def subscription_management_kb():
    keyboard = ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    keyboard.insert(KeyboardButton("📅 Дата отключения"))
    keyboard.insert(KeyboardButton("💵 Продлить"))
    keyboard.insert(KeyboardButton("🔙 Назад"))
    return keyboard


async def admin_main_kb():
    """Основное меню администратора"""
    keyboard = ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    keyboard.insert(KeyboardButton("👥 Статистика пользователей"))
    keyboard.insert(KeyboardButton("⏰ Статистика по датам"))
    keyboard.insert(KeyboardButton("➕ Продлить подписку"))
    keyboard.insert(KeyboardButton("♻️ Перезапустить WireGuard"))
    keyboard.insert(KeyboardButton("🔙 В главное меню"))
    return keyboard


async def admin_stats_filter_kb():
    """Клавиатура для фильтрации статистики"""
    keyboard = ReplyKeyboardMarkup(row_width=3, resize_keyboard=True)
    keyboard.insert(KeyboardButton("Все"))
    keyboard.insert(KeyboardButton("Активные"))
    keyboard.insert(KeyboardButton("Истекшие"))
    keyboard.insert(KeyboardButton("🔙 Назад"))
    return keyboard
