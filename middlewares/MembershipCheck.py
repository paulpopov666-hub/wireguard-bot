from aiogram import types
from aiogram.dispatcher.middlewares import BaseMiddleware
from loguru import logger

from data import configuration


class MembershipCheckMiddleware(BaseMiddleware):
    """
    Middleware для проверки подписки пользователя на обязательный канал.
    Если пользователь не состоит в канале, доступ к боту блокируется.
    """

    def __init__(self):
        super().__init__()
        self.channel_id = configuration.channel_id
        self.channel_invite_link = configuration.channel_invite_link

    async def on_pre_process_message(self, message: types.Message, data: dict):
        """Проверка подписки при получении сообщения"""
        # Пропускаем проверку для команд /start и администраторов
        if message.is_command() and message.text.startswith("/start"):
            return
        
        # Пропускаем проверку для администраторов
        if message.from_user.id in configuration.admins:
            return

        # Если канал не настроен, пропускаем проверку
        if not self.channel_id:
            logger.warning("CHANNEL_ID не настроен, проверка подписки отключена")
            return

        try:
            member = await message.bot.get_chat_member(
                chat_id=self.channel_id,
                user_id=message.from_user.id
            )
            
            # Проверяем статус участника
            if member.status in ["left", "kicked"]:
                # Пользователь вышел из канала или был удалён
                invite_link = self.channel_invite_link or "https://t.me/+acyqosqzppg2ZTM6"
                await message.answer(
                    f"⚠️ Вы вышли из нашего канала!\n\n"
                    f"Для продолжения использования бота, пожалуйста, вернитесь в канал:\n"
                    f"{invite_link}\n\n"
                    f"После возврата нажмите /start",
                    parse_mode=types.ParseMode.HTML,
                )
                from aiogram.dispatcher.handler import CancelHandler
                raise CancelHandler()
                
        except Exception as e:
            logger.error(f"Ошибка при проверке подписки: {e}")
            # В случае ошибки не блокируем пользователя, но логируем ошибку

    async def on_pre_process_callback_query(self, query: types.CallbackQuery, data: dict):
        """Проверка подписки при нажатии на callback кнопки"""
        # Пропускаем проверку для администраторов
        if query.from_user.id in configuration.admins:
            return

        # Если канал не настроен, пропускаем проверку
        if not self.channel_id:
            return

        try:
            member = await query.bot.get_chat_member(
                chat_id=self.channel_id,
                user_id=query.from_user.id
            )
            
            if member.status in ["left", "kicked"]:
                invite_link = self.channel_invite_link or "https://t.me/+acyqosqzppg2ZTM6"
                await query.answer(
                    f"⚠️ Вы вышли из канала! Вернитесь: {invite_link}",
                    show_alert=True
                )
                from aiogram.dispatcher.handler import CancelHandler
                raise CancelHandler()
                
        except Exception as e:
            logger.error(f"Ошибка при проверке подписки (callback): {e}")
