import asyncio
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from loguru import logger
import time

async def set_commands(dp):
    from aiogram import types

    await dp.bot.set_my_commands(
        commands=[
            types.BotCommand(command="/start", description="Запустить бота"),
            types.BotCommand(command="/support", description="Техническая поддержка"),
            types.BotCommand(command="/profile", description="Мой профиль"),
        ]
    )


async def on_startup(dp):
    import handlers
    import middlewares
    from utils.watchdog import Watchdog
    from database.migrate_v2 import run_migration

    # Запуск миграции БД
    try:
        await run_migration()
        logger.info("✅ Миграция базы данных выполнена")
    except Exception as e:
        logger.warning(f"⚠️ Ошибка миграции (возможно уже выполнена): {e}")

    middlewares.setup(dp)
    await set_commands(dp)
    handlers.setup(dp)

    logger.add(
        f'logs/{time.strftime("%Y-%m-%d__%H-%M")}.log',
        level="DEBUG",
        rotation="500 MB",
        compression="zip",
    )

    daemon = Watchdog()
    daemon.run()
    logger.success("[+] Bot started successfully")


async def main():
    from data.config import BOT_TOKEN
    from handlers import dp
    
    bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher(bot=bot)
    
    await on_startup(dp)
    await dp.start_polling(bot, skip_updates=True)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
