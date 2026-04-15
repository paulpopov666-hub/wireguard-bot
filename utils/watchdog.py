# ASYNC daemon that watches for users who have a subscription end date and sends them a message
# first time : 2 days before end date
# second time : 1 day before end date
# third time : end date
# fourth time : 1 day after end date send kb free user and disconnect from VPN

from loguru import logger
from database.selector import get_user_ids_enddate_n_days, get_all_expired_user_ids
import keyboards as kb
from loader import bot
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from loader import vpn_config


class Watchdog:
    def __init__(self):
        self.scheduler = AsyncIOScheduler()

    def run(self):
        """start watchdog coroutine every hour at minute 0"""
        # Check every hour instead of once a day for more responsive disconnection
        self.scheduler.add_job(self.check_end_date, "cron", minute=0)
        self.scheduler.start()
        logger.success("[+] Watchdog coroutine created and started successfully")

    async def check_end_date(self):
        logger.info("[+] Checking for users with end date")
        notified_users = set()
        
        # Check users whose subscription ends in 2, 1, 0 days
        for days in range(0, 3):
            user_ids = get_user_ids_enddate_n_days(days)
            if user_ids:
                for user_id in user_ids:
                    if user_id not in notified_users:
                        message_text = self.get_message_text(days)
                        await bot.send_message(user_id, message_text)
                        notified_users.add(user_id)
                        logger.warning(
                            f"[+] user {user_id} notified about end date {days} days"
                        )

        # Check users whose subscription has expired (including those expired long ago)
        expired_user_ids = get_all_expired_user_ids()
        if expired_user_ids:
            for user_id in expired_user_ids:
                if user_id not in notified_users:
                    message_text = self.get_message_text(-1)
                    try:
                        await bot.send_message(
                            user_id,
                            message_text,
                            reply_markup=await kb.reply.free_user_kb(user_id=user_id),
                        )
                    except Exception as e:
                        logger.error(f"[-] Failed to send message to user {user_id}: {e}")
                    
                    # Properly await the async disconnect function
                    try:
                        await vpn_config.disconnect_peer(user_id)
                        notified_users.add(user_id)
                        logger.warning(
                            f"[+] user {user_id} disconnected - subscription expired"
                        )
                    except Exception as e:
                        logger.error(f"[-] Failed to disconnect user {user_id}: {e}")

        logger.info("Finished checking for users with end date")

    def get_message_text(self, days: int) -> str:
        if days == -1:
            return "Ваша подписка закончилась, но вы можете продлить ее =)"
        elif days == 0:
            return "Сегодня заканчивается ваша подписка, не забудьте продлить ее =)"
        elif days == 1:
            return "Ваша подписка заканчивается завтра, не забудьте продлить ее =)"
        elif days == 2:
            return "Ваша подписка заканчивается через 2 дня, не забудьте продлить ее =)"

    def stop(self):
        self.scheduler.shutdown()
