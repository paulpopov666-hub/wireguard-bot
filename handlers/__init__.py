from .user import *
from .admin import *
from aiogram.types import ContentType

# DON'T TOUCH THIS IMPORT
from loader import dp
from aiogram import Dispatcher


def setup(dp: Dispatcher):
    """setup handlers for users and moders in one place and add throttling in 5 seconds

    Args:
        dp (Dispatcher): Dispatcher object
    """

    """user handlers"""
    dp.register_message_handler(cmd_start, commands=["start"], state=None)

    dp.register_message_handler(
        cmd_pay, lambda message: message.text.startswith("💵"), state=None
    )

    dp.register_message_handler(
        successful_payment_handler, content_types=ContentType.SUCCESSFUL_PAYMENT
    )

    dp.register_message_handler(cmd_my_configs, text="📁 Мои конфиги", state=None)

    dp.register_message_handler(cmd_menu, text="🔙 Назад", state=None)
    
    dp.register_message_handler(cmd_menu_admin, text="🔙 В главное меню", state=None)

    dp.register_callback_query_handler(
        device_selected,
        lambda call: call.data.endswith("config_create_request"),
        state=NewConfig.device,
    )

    dp.register_callback_query_handler(
        cancel_config_creation,
        lambda call: call.data == "cancel_config_creation",
        state=NewConfig.device,
    )

    dp.register_message_handler(create_new_config, text="🆕 Создать конфиг", state=None)

    dp.register_message_handler(
        cmd_show_config, lambda message: message.text.startswith("🔐"), state=None
    )

    dp.register_message_handler(
        cmd_support,
        text="📝 Помощь",
    )

    dp.register_message_handler(
        cmd_show_end_time,
        text="📅 Дата отключения",
    )

    dp.register_message_handler(
        cmd_show_subscription,
        text="🕑 Моя подписка",
    )

    dp.register_message_handler(
        cmd_check_channel_subscription,
        text="✅ Проверить подписку",
        state=None
    )
    
    dp.register_message_handler(
        cmd_refresh_status,
        text="♻️ Обновить статус",
        state=None
    )

    dp.register_message_handler(
        got_payment_screenshot,
        state=NewPayment.payment_image,
        content_types=ContentType.ANY,
    )

    dp.register_callback_query_handler(
        cancel_payment,
        lambda call: call.data == "cancel_payment",
        state=NewPayment.payment_image,
    )

    """admin handlers"""
    # Admin menu command
    dp.register_message_handler(cmd_admin_menu, commands=["admin"], state=None)
    
    # Admin button handlers
    dp.register_message_handler(
        cmd_admin_stats_users, 
        text="👥 Статистика пользователей", 
        state=None
    )
    
    dp.register_message_handler(
        cmd_admin_stats_dates, 
        text="⏰ Статистика по датам", 
        state=None
    )
    
    dp.register_message_handler(
        cmd_admin_give_subscription, 
        text="➕ Продлить подписку", 
        state=None
    )
    
    dp.register_message_handler(
        cmd_admin_restart_wg, 
        text="♻️ Перезапустить WireGuard", 
        state=None
    )
    
    # Stats filter handlers
    dp.register_message_handler(
        cmd_admin_stats_all,
        text="Все",
        state=None
    )
    
    dp.register_message_handler(
        cmd_admin_stats_active,
        text="Активные",
        state=None
    )
    
    dp.register_message_handler(
        cmd_admin_stats_expired,
        text="Истекшие",
        state=None
    )

    # Legacy command handlers (for backward compatibility)
    dp.register_message_handler(cmd_info, commands=["info"], state=None)

    dp.register_message_handler(statistic_endtime, commands=["stats"], state=None)

    dp.register_message_handler(give_subscription_time, commands=["give"], state=None)

    dp.register_message_handler(
        restart_wg_service_admin, commands=["wgrestart"], state=None
    )
