# ASYNC daemon that watches for users who have a subscription end date and sends them a message
# first time : 3 days before end date
# second time : 2 days before end date
# third time : 1 day before end date
# fourth time : end date (subscription expired, disconnect peer)
# then: every 3 hours send reminder if subscription is expired

from loguru import logger
from database.selector import get_user_ids_enddate_n_days, get_all_user_ids_and_enddate, is_subscription_expired
from database.update import update_last_notification_sent, get_last_notification_sent
import keyboards as kb
from loader import bot
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from loader import vpn_config
from datetime import datetime, timedelta
from data import configuration


class Watchdog:
    def __init__(self):
        self.scheduler = AsyncIOScheduler()

    def run(self):
        """start watchdog coroutine every hour"""
        # Check every hour for subscription reminders
        self.scheduler.add_job(self.check_end_date, "cron", minute=0)
        # Check every 3 hours for expired subscriptions
        self.scheduler.add_job(self.check_expired_subscriptions, "cron", minute=0, hour="*/3")
        # Check daily for group membership
        if configuration.required_group_id:
            self.scheduler.add_job(self.check_group_membership, "cron", hour=3, minute=0)
        self.scheduler.start()
        logger.success("[+] Watchdog coroutine created and started successfully")

    async def check_end_date(self):
        """Check for users with subscription ending in 3, 2, or 1 day and send reminders"""
        logger.info("[+] Checking for users with end date approaching")
        
        for days in [3, 2, 1]:  # 3, 2, 1 days before expiration
            user_ids = get_user_ids_enddate_n_days(days)
            if not user_ids:
                continue
                
            for user_id in user_ids:
                # Check if already notified for this period (within last 23 hours)
                last_notif = get_last_notification_sent(user_id)
                if last_notif and self._is_notified_for_period(last_notif, days):
                    logger.info(f"[+] user {user_id} already notified for {days} days period")
                    continue
                    
                message_text = self.get_message_text(days)
                await bot.send_message(user_id, message_text)
                update_last_notification_sent(user_id)
                logger.warning(
                    f"[+] user {user_id} notified about end date in {days} days"
                )

        logger.info("Finished checking for users with end date approaching")

    async def check_expired_subscriptions(self):
        """Check for expired subscriptions and send reminders every 3 hours"""
        logger.info("[+] Checking for expired subscriptions")
        
        all_users = get_all_user_ids_and_enddate()
        if not all_users:
            return
            
        for user_id, end_date in all_users:
            if end_date < datetime.now():
                # Subscription is expired
                last_notif = get_last_notification_sent(user_id)
                
                # If never notified after expiration or last notification was more than 3 hours ago
                should_notify = False
                if last_notif is None:
                    should_notify = True
                elif datetime.now() - last_notif >= timedelta(hours=3):
                    should_notify = True
                
                if should_notify:
                    message_text = self.get_message_text(-1)  # expired message
                    try:
                        await bot.send_message(
                            user_id,
                            message_text,
                            reply_markup=await kb.reply.free_user_kb(user_id=user_id),
                        )
                        update_last_notification_sent(user_id)
                        logger.warning(
                            f"[+] user {user_id} notified about expired subscription"
                        )
                    except Exception as e:
                        logger.error(f"[-] Failed to send message to user {user_id}: {e}")

    def _is_notified_for_period(self, last_notif: datetime, days: int) -> bool:
        """Check if user was already notified for specific days period
        
        Args:
            last_notif: timestamp of last notification
            days: days until expiration (1, 2, or 3)
            
        Returns:
            True if user was already notified for this specific period
        """
        if not last_notif:
            return False
            
        # Calculate when the notification for this period should have been sent
        # For 3 days before: notification should be sent when there are exactly 3 days left
        # For 2 days before: notification should be sent when there are exactly 2 days left
        # For 1 day before: notification should be sent when there is exactly 1 day left
        
        # We check if the last notification was sent within a reasonable window for this period
        # A notification for "N days before" is valid if it was sent within the last 24 hours
        # and the subscription end date is actually N days from now
        
        time_since_notification = datetime.now() - last_notif
        
        # If notification was sent less than 23 hours ago, consider it as already notified
        # for this run cycle to prevent duplicate notifications within the same day
        if time_since_notification < timedelta(hours=23):
            return True
            
        return False

    def get_message_text(self, days: int) -> str:
        if days == -1:
            return "⚠️ Ваша подписка закончилась! Продлите подписку, чтобы продолжить пользоваться VPN.\n\nДля продления нажмите кнопку ниже."
        elif days == 1:
            return "⏰ Ваша подписка заканчивается завтра! Не забудьте продлить её, чтобы не потерять доступ к VPN."
        elif days == 2:
            return "📅 Ваша подписка заканчивается через 2 дня. Рекомендуем продлить её заранее."
        elif days == 3:
            return "🔔 Напоминаем: ваша подписка заканчивается через 3 дня. Продлите подписку, чтобы продолжить пользоваться VPN без перерывов."
        return ""

    async def check_group_membership(self):
        """Check daily if users are still members of the required group"""
        if not configuration.required_group_id:
            return
            
        logger.info("[+] Checking group membership for all users")
        
        all_users = get_all_user_ids_and_enddate()
        if not all_users:
            return
        
        for user_id, end_date in all_users:
            try:
                member = await bot.get_chat_member(configuration.required_group_id, user_id)
                if member.status not in ['member', 'administrator', 'creator']:
                    # User left the group - ban them
                    logger.warning(f"[+] User {user_id} left the required group, banning...")
                    
                    # Disconnect VPN peer
                    try:
                        await vpn_config.disconnect_peer(user_id)
                    except Exception as e:
                        logger.error(f"Failed to disconnect peer {user_id}: {e}")
                    
                    # Notify user
                    try:
                        await bot.send_message(
                            user_id,
                            "❌ Вы вышли из нашей группы. Доступ к VPN приостановлен.\n"
                            "Вернитесь в группу и напишите /start для восстановления доступа."
                        )
                    except Exception as e:
                        logger.error(f"Failed to notify user {user_id} about group leave: {e}")
                        
            except Exception as e:
                logger.error(f"Failed to check group membership for user {user_id}: {e}")
                continue
        
        logger.info("[+] Group membership check completed")

    def stop(self):
        self.scheduler.shutdown()
