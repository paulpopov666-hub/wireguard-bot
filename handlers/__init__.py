from .user import *
from .admin import *
from .admin_extended import *
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
        cmd_reboot_wg_service,
        text="☢️Перезагрузить VPN",
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
    
    # Handler for "I joined the group" button
    dp.register_message_handler(
        handle_joined_group,
        text="✅ Я вступил в группу",
        state=None,
    )

    """moder handlers"""
    dp.register_message_handler(cmd_info, commands=["info"], state=None)

    dp.register_message_handler(statistic_endtime, commands=["stats"], state=None)

    dp.register_message_handler(give_subscription_time, commands=["give"], state=None)

    dp.register_message_handler(
        restart_wg_service_admin, commands=["wgrestart"], state=None
    )

    """extended admin handlers"""
    # Obfuscation management
    dp.register_message_handler(cmd_set_obfuscation, commands=['set_obfuscation'])
    dp.register_callback_query_handler(select_obfuscation_param, text_startswith='obf_')
    
    # Statistics
    dp.register_message_handler(cmd_stats, commands=['stats'])
    
    # Broadcast
    dp.register_message_handler(cmd_broadcast, commands=['broadcast'])
    dp.register_callback_query_handler(select_broadcast_audience, text_startswith='broadcast_')
    dp.register_message_handler(send_broadcast, state=AdminBroadcast.message)
    
    # Support tickets
    dp.register_message_handler(handle_support_request, commands=['support'])
    dp.register_message_handler(cmd_support_tickets, commands=['tickets'])
    
    # Maintenance mode
    dp.register_message_handler(cmd_maintenance_mode, commands=['maintenance'])
