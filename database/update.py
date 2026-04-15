import psycopg2 as pg
from loguru import logger
from data import configuration
from datetime import datetime, timedelta


def update_user_payment(user_id: int) -> None:
    """
    Update user payment end date in table users
    add 30 days to current date if user don't have subscription at the moment
    and add 30 days to date in subscription_end_date if user have not expired subscription now
    """
    try:
        conn = pg.connect(**configuration.db_connection_parameters)
        with conn.cursor() as cursor:
            cursor.execute(
                """--sql
                UPDATE users SET subscription_end_date = CASE
                WHEN subscription_end_date < %s THEN %s + %s
                ELSE subscription_end_date + %s END
                WHERE user_id = %s
                """,
                (
                    datetime.now(),
                    datetime.now(),
                    timedelta(days=30),
                    timedelta(days=30),
                    user_id,
                ),
            )

            conn.commit()

            # get username for log
            cursor.execute(
                """--sql
                SELECT username FROM users WHERE user_id = %s
                """,
                (user_id,),
            )
            username = cursor.fetchone()[0]

            logger.info(
                f"[+] user {user_id}::{username} payment updated; added: 30 days"
            )
    except (Exception, pg.DatabaseError) as error:
        logger.error(f"[-] {error}")
        return None


def update_user_config_count(user_id: int) -> None:
    """Update user config count in table users
    add 1 to current config count"""
    try:
        conn = pg.connect(**configuration.db_connection_parameters)
        with conn.cursor() as cursor:
            cursor.execute(
                """--sql
                UPDATE users SET config_count = config_count + 1 WHERE user_id = %s
                """,
                (user_id,),
            )

            conn.commit()
            logger.info(f"[+] user {user_id} config count updated to {cursor.rowcount}")
    except (Exception, pg.DatabaseError) as error:
        logger.error(f"[-] {error}")
        return None


def update_given_subscription_time(user_id: int, days: int) -> None:
    """Update user payment end date in table users
    add given days to date in table if user have not expired subscription now
    else add given days to current date"""
    try:
        conn = pg.connect(**configuration.db_connection_parameters)
        with conn.cursor() as cursor:
            cursor.execute(
                """--sql
                UPDATE users SET subscription_end_date = CASE
                WHEN subscription_end_date < %s THEN %s + %s
                ELSE subscription_end_date + %s END
                WHERE user_id = %s
                """,
                (
                    datetime.now(),
                    datetime.now(),
                    timedelta(days=days),
                    timedelta(days=days),
                    user_id,
                ),
            )

            conn.commit()

            # get username for log
            cursor.execute(
                """--sql
                SELECT username FROM users WHERE user_id = %s
                """,
                (user_id,),
            )
            username = cursor.fetchone()[0]

            logger.info(
                f"[+] user {user_id}::{username} payment updated [BY ADMIN]; added: {days} days"
            )
    except (Exception, pg.DatabaseError) as error:
        logger.error(f"[-] {error}")
        return None


def set_user_enddate_to_n(user_id: int, days: int) -> None:
    """Update user payment end date in table users
    set date to datetime.now() + N days"""
    try:
        conn = pg.connect(**configuration.db_connection_parameters)
        with conn.cursor() as cursor:
            cursor.execute(
                """--sql
                UPDATE users SET subscription_end_date = %s WHERE user_id = %s
                """,
                (datetime.now() + timedelta(days=days), user_id),
            )

            conn.commit()

            # get username for log
            cursor.execute(
                """--sql
                SELECT username FROM users WHERE user_id = %s
                """,
                (user_id,),
            )
            username = cursor.fetchone()[0]

            logger.info(
                f"""[+] user {user_id}::{username} payment updated [BY ADMIN]; set to:
                {datetime.now() + timedelta(days=days)}"""
            )
    except (Exception, pg.DatabaseError) as error:
        logger.error(f"[-] {error}")
        return None


def update_last_notification_sent(user_id: int) -> None:
    """Update last_notification_sent timestamp for user"""
    try:
        conn = pg.connect(**configuration.db_connection_parameters)
        with conn.cursor() as cursor:
            cursor.execute(
                """--sql
                UPDATE users SET last_notification_sent = %s WHERE user_id = %s
                """,
                (datetime.now(), user_id),
            )

            conn.commit()
            logger.info(f"[+] user {user_id} last_notification_sent updated")
    except (Exception, pg.DatabaseError) as error:
        logger.error(f"[-] {error}")
        return None


def get_last_notification_sent(user_id: int) -> datetime | None:
    """Get last_notification_sent timestamp for user"""
    try:
        conn = pg.connect(**configuration.db_connection_parameters)
        with conn.cursor() as cursor:
            cursor.execute(
                """--sql
                SELECT last_notification_sent FROM users WHERE user_id = %s
                """,
                (user_id,),
            )
            result = cursor.fetchone()[0]
            return result
    except (Exception, pg.DatabaseError) as error:
        logger.error(f"[-] {error}")
        return None


def is_trial_used(user_id: int) -> bool:
    """Check if user has already used trial period"""
    try:
        conn = pg.connect(**configuration.db_connection_parameters)
        with conn.cursor() as cursor:
            cursor.execute(
                """--sql
                SELECT trial_used FROM users WHERE user_id = %s
                """,
                (user_id,),
            )
            result = cursor.fetchone()
            return result[0] if result else False
    except (Exception, pg.DatabaseError) as error:
        logger.error(f"[-] {error}")
        return False


def set_trial_used(user_id: int) -> None:
    """Set trial_used to True for user"""
    try:
        conn = pg.connect(**configuration.db_connection_parameters)
        with conn.cursor() as cursor:
            cursor.execute(
                """--sql
                UPDATE users SET trial_used = TRUE WHERE user_id = %s
                """,
                (user_id,),
            )
            conn.commit()
            logger.info(f"[+] user {user_id} trial_used set to TRUE")
    except (Exception, pg.DatabaseError) as error:
        logger.error(f"[-] {error}")
        return None


def add_referral_bonus_days(user_id: int, days: int) -> None:
    """Add bonus days to user's subscription for referral
    
    Args:
        user_id: User ID to add bonus days to
        days: Number of days to add
    """
    try:
        conn = pg.connect(**configuration.db_connection_parameters)
        with conn.cursor() as cursor:
            # Add days to subscription_end_date
            cursor.execute(
                """--sql
                UPDATE users SET subscription_end_date = subscription_end_date + %s,
                referral_bonus_days = referral_bonus_days + %s
                WHERE user_id = %s
                """,
                (timedelta(days=days), days, user_id),
            )
            conn.commit()
            
            # Get username for log
            cursor.execute(
                """--sql
                SELECT username FROM users WHERE user_id = %s
                """,
                (user_id,),
            )
            username = cursor.fetchone()[0]
            
            logger.info(f"[+] user {user_id}::{username} received {days} referral bonus days")
    except (Exception, pg.DatabaseError) as error:
        logger.error(f"[-] {error}")
        return None


def get_referrer_user_id(user_id: int) -> int | None:
    """Get the user_id of the referrer for a given user
    
    Args:
        user_id: User ID to get referrer for
        
    Returns:
        Referrer user_id or None if no referrer
    """
    try:
        conn = pg.connect(**configuration.db_connection_parameters)
        with conn.cursor() as cursor:
            cursor.execute(
                """--sql
                SELECT referred_by FROM users WHERE user_id = %s
                """,
                (user_id,),
            )
            result = cursor.fetchone()
            return result[0] if result else None
    except (Exception, pg.DatabaseError) as error:
        logger.error(f"[-] {error}")
        return None
