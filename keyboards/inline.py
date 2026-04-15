from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from database import selector as select


async def device_kb(user_id: int):
    """returns inline keyboard with various options of cfg choosing"""
    kb = InlineKeyboardMarkup(
        row_width=2,
    )

    existing_devices = [
        item[0].split("_")[-1] for item in select.all_user_configs(user_id=user_id)
    ]
    
    # Check if user has reached max configs (10)
    config_count = select.get_user_config_count(user_id=user_id)
    max_configs = 10
    
    if config_count >= max_configs:
        kb.add(
            InlineKeyboardButton(text="⚠️ Лимит конфигов (10/10)", callback_data="config_limit_reached")
        )
        return kb

    # Add button to create next config number
    next_config_num = config_count + 1
    kb.insert(
        InlineKeyboardButton(text=f"➕ Создать конфиг #{next_config_num}", callback_data="create_config")
    )

    kb.add(
        InlineKeyboardButton(text="❌Отмена❌", callback_data="cancel_config_creation")
    )

    return kb


async def cancel_payment_kb():
    """returns inline keyboard with cancel payment button"""
    kb = InlineKeyboardMarkup(row_width=1)
    kb.add(InlineKeyboardButton(text="❌Отмена❌", callback_data="cancel_payment"))
    return kb


async def config_limit_kb():
    """returns inline keyboard when config limit is reached"""
    kb = InlineKeyboardMarkup(row_width=1)
    kb.add(InlineKeyboardButton(text="🔙 Назад", callback_data="cancel_config_creation"))
    return kb


async def confirm_new_config_kb():
    """returns inline keyboard for confirming new config creation"""
    kb = InlineKeyboardMarkup(row_width=2)
    kb.add(
        InlineKeyboardButton(text="✅ Да, создать", callback_data="confirm_new_config"),
        InlineKeyboardButton(text="❌ Отмена", callback_data="cancel_new_config")
    )
    return kb


if __name__ == "__main__":
    ...
