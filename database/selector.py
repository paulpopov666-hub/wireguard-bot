import psycopg2 as pg
from loguru import logger
from data import configuration
from datetime import datetime, timedelta


def is_exist_user(user_id: int) -> bool:
    """Check if user is exist in database"""
    try:
        conn = pg.connect(**configuration.db_connection_parameters)
        with conn.cursor() as cursor:
            cursor.execute(
                """--sql
                SELECT EXISTS(SELECT 1 FROM users WHERE user_id = %s)
                """,
                (user_id,),
            )
            return cursor.fetchone()[0]

    except (Exception, pg.DatabaseError) as error:
        logger.error(f"[-] {error}")
        return False


def is_user_have_config(user_id: int) -> bool:
    """Check if user have config in database"""
    try:
        conn = pg.connect(**configuration.db_connection_parameters)
        with conn.cursor() as cursor:
            cursor.execute(
                """--sql
                SELECT EXISTS(SELECT 1 FROM vpn_config WHERE user_id = %s)
                """,
                (user_id,),
            )
            return cursor.fetchone()[0]
    except (Exception, pg.DatabaseError) as error:
        logger.error(f"[-] {error}")
        return False


def all_user_configs(user_id: int) -> list[str] | bool:
    """Get all user configs"""
    try:
        conn = pg.connect(**configuration.db_connection_parameters)
        with conn.cursor() as cursor:
            cursor.execute(
                """--sql
                SELECT config_name FROM vpn_config WHERE user_id = %s
                """,
                (user_id,),
            )
            return cursor.fetchall()
    except (Exception, pg.DatabaseError) as error:
        logger.error(f"[-] {error}")
        return False


def is_subscription_end(user_id: int) -> bool:
    """Check if user subscription is end"""
    try:
        conn = pg.connect(**configuration.db_connection_parameters)
        with conn.cursor() as cursor:
            cursor.execute(
                """--sql
                SELECT subscription_end_date FROM users WHERE user_id = %s
                """,
                (user_id,),
            )
            date = cursor.fetchone()[0]
            return date < datetime.now()
    except (Exception, pg.DatabaseError) as error:
        logger.error(f"[-] {error}")
        return False


def get_subscription_end_date(user_id: int) -> datetime | bool:
    """Get user subscription end date"""
    try:
        conn = pg.connect(**configuration.db_connection_parameters)
        with conn.cursor() as cursor:
            cursor.execute(
                """--sql
                SELECT subscription_end_date FROM users WHERE user_id = %s
                """,
                (user_id,),
            )
            # return date in format: day-month-year
            return cursor.fetchone()[0].strftime("%d-%m-%Y")
    except (Exception, pg.DatabaseError) as error:
        logger.error(f"[-] {error}")
        return False


def get_user_config(user_id: int, config_name: str) -> str | bool:
    """Get user config"""
    try:
        conn = pg.connect(**configuration.db_connection_parameters)
        with conn.cursor() as cursor:
            cursor.execute(
                """--sql
                SELECT config FROM vpn_config WHERE user_id = %s AND config_name = %s
                """,
                (user_id, config_name),
            )
            return cursor.fetchone()[0]
    except (Exception, pg.DatabaseError) as error:
        logger.error(f"[-] {error}")
        return False


def get_all_usernames_and_enddate() -> list | bool:
    """Get all usernames and subscription end date"""
    try:
        conn = pg.connect(**configuration.db_connection_parameters)
        with conn.cursor() as cursor:
            cursor.execute(
                """--sql
                SELECT username, subscription_end_date FROM users
                """
            )
            return cursor.fetchall()
    except (Exception, pg.DatabaseError) as error:
        logger.error(f"[-] {error}")
        return False


def get_all_user_ids_and_enddate() -> list | bool:
    """Get all user_ids and subscription end date"""
    try:
        conn = pg.connect(**configuration.db_connection_parameters)
        with conn.cursor() as cursor:
            cursor.execute(
                """--sql
                SELECT user_id, subscription_end_date FROM users
                """
            )
            return cursor.fetchall()
    except (Exception, pg.DatabaseError) as error:
        logger.error(f"[-] {error}")
        return False


def get_user_ids_and_enddate() -> list | bool:
    """Get all user_ids and subscription end date (alias for get_all_user_ids_and_enddate)"""
    return get_all_user_ids_and_enddate()


def get_user_id(username: str) -> int:
    """Get user id"""
    try:
        conn = pg.connect(**configuration.db_connection_parameters)
        with conn.cursor() as cursor:
            cursor.execute(
                """--sql
                SELECT user_id FROM users WHERE username = %s
                """,
                (username,),
            )
            return cursor.fetchone()[0]
    except (Exception, pg.DatabaseError) as error:
        logger.error(f"[-] {error}")
        return False


def get_all_user_ids() -> list[int] | bool:
    """Get all user ids"""
    try:
        conn = pg.connect(**configuration.db_connection_parameters)
        with conn.cursor() as cursor:
            cursor.execute(
                """--sql
                SELECT user_id FROM users
                """
            )
            return cursor.fetchall()
    except (Exception, pg.DatabaseError) as error:
        logger.error(f"[-] {error}")
        return False


def get_user_ids_enddate_n_days(days: int) -> list[int] | bool:
    """Get user ids where subscription ends in N days
    don't watch at hours, minutes, seconds, milliseconds
    """
    match days:
        case 0:
            shift = timedelta(days=1)
        case -1:
            shift = timedelta(days=2)
        case _:
            shift = timedelta(days=0)

    try:
        conn = pg.connect(**configuration.db_connection_parameters)
        with conn.cursor() as cursor:
            cursor.execute(
                """--sql
                SELECT user_id FROM users WHERE subscription_end_date BETWEEN %s AND %s
                """,
                (datetime.now() - shift, datetime.now() + timedelta(days=days)),
            )
            return [item[0] for item in cursor.fetchall()]
    except (Exception, pg.DatabaseError) as error:
        logger.error(f"[-] {error}")
        return False


def get_username_by_id(user_id: int) -> str | bool:
    """Get username by user id"""
    try:
        conn = pg.connect(**configuration.db_connection_parameters)
        with conn.cursor() as cursor:
            cursor.execute(
                """--sql
                SELECT username FROM users WHERE user_id = %s
                """,
                (user_id,),
            )
            return cursor.fetchone()[0]
    except (Exception, pg.DatabaseError) as error:
        logger.error(f"[-] {error}")
        return False


def is_subscription_expired(user_id: int) -> bool:
    """Check if user subscription is expired"""
    try:
        conn = pg.connect(**configuration.db_connection_parameters)
        with conn.cursor() as cursor:
            cursor.execute(
                """--sql
                SELECT subscription_end_date FROM users WHERE user_id = %s
                """,
                (user_id,),
            )
            date = cursor.fetchone()[0]
            return date < datetime.now()
    except (Exception, pg.DatabaseError) as error:
        logger.error(f"[-] {error}")
        return False


# Новые методы для расширенного функционала

def count_all_users() -> int:
    """Подсчитать общее количество пользователей"""
    try:
        conn = pg.connect(**configuration.db_connection_parameters)
        with conn.cursor() as cursor:
            cursor.execute("SELECT COUNT(*) FROM users")
            return cursor.fetchone()[0]
    except (Exception, pg.DatabaseError) as error:
        logger.error(f"[-] {error}")
        return 0


def count_active_subscriptions() -> int:
    """Подсчитать пользователей с активной подпиской"""
    try:
        conn = pg.connect(**configuration.db_connection_parameters)
        with conn.cursor() as cursor:
            cursor.execute(
                """--sql
                SELECT COUNT(*) FROM users 
                WHERE subscription_end_date > NOW()
                """
            )
            return cursor.fetchone()[0]
    except (Exception, pg.DatabaseError) as error:
        logger.error(f"[-] {error}")
        return 0


def count_trial_users() -> int:
    """Подсчитать пользователей на триале"""
    try:
        conn = pg.connect(**configuration.db_connection_parameters)
        with conn.cursor() as cursor:
            cursor.execute(
                """--sql
                SELECT COUNT(*) FROM users 
                WHERE trial_used = 1 
                AND subscription_end_date <= NOW()
                """
            )
            return cursor.fetchone()[0]
    except (Exception, pg.DatabaseError) as error:
        logger.error(f"[-] {error}")
        return 0


def get_revenue_by_period(days: int = 30) -> float:
    """Получить выручку за период в днях"""
    try:
        conn = pg.connect(**configuration.db_connection_parameters)
        with conn.cursor() as cursor:
            cursor.execute(
                """--sql
                SELECT COALESCE(SUM(amount), 0) FROM payments
                WHERE status = 'paid'
                AND created_at >= NOW() - INTERVAL '%s days'
                """,
                (days,)
            )
            return cursor.fetchone()[0]
    except (Exception, pg.DatabaseError) as error:
        logger.error(f"[-] {error}")
        return 0.0


def count_paid_from_trial() -> int:
    """Подсчитать пользователей, перешедших из триала в оплату"""
    try:
        conn = pg.connect(**configuration.db_connection_parameters)
        with conn.cursor() as cursor:
            cursor.execute(
                """--sql
                SELECT COUNT(DISTINCT user_id) FROM payments p
                JOIN users u ON p.user_id = u.user_id
                WHERE u.trial_used = 1
                """
            )
            return cursor.fetchone()[0]
    except (Exception, pg.DatabaseError) as error:
        logger.error(f"[-] {error}")
        return 0


def count_all_configs() -> int:
    """Подсчитать общее количество конфигов"""
    try:
        conn = pg.connect(**configuration.db_connection_parameters)
        with conn.cursor() as cursor:
            cursor.execute("SELECT COUNT(*) FROM vpn_config")
            return cursor.fetchone()[0]
    except (Exception, pg.DatabaseError) as error:
        logger.error(f"[-] {error}")
        return 0


def count_active_configs() -> int:
    """Подсчитать активные конфиги"""
    try:
        conn = pg.connect(**configuration.db_connection_parameters)
        with conn.cursor() as cursor:
            cursor.execute(
                """--sql
                SELECT COUNT(*) FROM vpn_config vc
                JOIN users u ON vc.user_id = u.user_id
                WHERE u.subscription_end_date > NOW()
                """
            )
            return cursor.fetchone()[0]
    except (Exception, pg.DatabaseError) as error:
        logger.error(f"[-] {error}")
        return 0


def get_users_by_segment(segment: str) -> list:
    """Получить пользователей по сегменту для рассылки"""
    try:
        conn = pg.connect(**configuration.db_connection_parameters)
        with conn.cursor() as cursor:
            if segment == 'all':
                cursor.execute("SELECT user_id FROM users")
            elif segment == 'expiring':
                cursor.execute(
                    """--sql
                    SELECT user_id FROM users
                    WHERE subscription_end_date BETWEEN NOW() AND NOW() + INTERVAL '3 days'
                    """
                )
            elif segment == 'paid':
                cursor.execute(
                    """--sql
                    SELECT user_id FROM users
                    WHERE subscription_end_date > NOW()
                    """
                )
            elif segment == 'trial':
                cursor.execute(
                    """--sql
                    SELECT user_id FROM users
                    WHERE trial_used = 1 AND subscription_end_date <= NOW()
                    """
                )
            else:
                cursor.execute("SELECT user_id FROM users")
            
            return [row[0] for row in cursor.fetchall()]
    except (Exception, pg.DatabaseError) as error:
        logger.error(f"[-] {error}")
        return []


def get_open_tickets() -> list:
    """Получить открытые тикеты поддержки"""
    try:
        conn = pg.connect(**configuration.db_connection_parameters)
        with conn.cursor() as cursor:
            cursor.execute(
                """--sql
                SELECT id, user_id, message_text, created_at 
                FROM tickets
                WHERE status = 'open'
                ORDER BY created_at ASC
                """
            )
            return cursor.fetchall()
    except (Exception, pg.DatabaseError) as error:
        logger.error(f"[-] {error}")
        return []


def get_setting(key: str) -> str | None:
    """Получить значение настройки"""
    try:
        conn = pg.connect(**configuration.db_connection_parameters)
        with conn.cursor() as cursor:
            cursor.execute(
                "SELECT value FROM settings WHERE key = %s",
                (key,)
            )
            result = cursor.fetchone()
            return result[0] if result else None
    except (Exception, pg.DatabaseError) as error:
        logger.error(f"[-] {error}")
        return None


def update_setting(key: str, value: str):
    """Обновить значение настройки"""
    try:
        conn = pg.connect(**configuration.db_connection_parameters)
        with conn.cursor() as cursor:
            cursor.execute(
                """--sql
                INSERT INTO settings (key, value) 
                VALUES (%s, %s)
                ON CONFLICT (key) DO UPDATE SET value = EXCLUDED.value
                """,
                (key, value)
            )
            conn.commit()
    except (Exception, pg.DatabaseError) as error:
        logger.error(f"[-] {error}")
        conn.rollback()


def get_promo_code(code: str) -> dict | None:
    """Получить информацию о промокоде"""
    try:
        conn = pg.connect(**configuration.db_connection_parameters)
        with conn.cursor() as cursor:
            cursor.execute(
                """--sql
                SELECT code, bonus_days, usage_count, max_usages, is_active
                FROM promo_codes
                WHERE code = %s
                """,
                (code,)
            )
            result = cursor.fetchone()
            if result:
                return {
                    'code': result[0],
                    'bonus_days': result[1],
                    'usage_count': result[2],
                    'max_usages': result[3],
                    'is_active': result[4]
                }
            return None
    except (Exception, pg.DatabaseError) as error:
        logger.error(f"[-] {error}")
        return None


def create_promo_code(code: str, bonus_days: int, max_usages: int = 0):
    """Создать новый промокод"""
    try:
        conn = pg.connect(**configuration.db_connection_parameters)
        with conn.cursor() as cursor:
            cursor.execute(
                """--sql
                INSERT INTO promo_codes (code, bonus_days, max_usages, is_active)
                VALUES (%s, %s, %s, 1)
                """,
                (code, bonus_days, max_usages)
            )
            conn.commit()
    except (Exception, pg.DatabaseError) as error:
        logger.error(f"[-] {error}")
        conn.rollback()


def get_user_username(user_id: int) -> str | None:
    """Получить username пользователя"""
    try:
        conn = pg.connect(**configuration.db_connection_parameters)
        with conn.cursor() as cursor:
            cursor.execute(
                "SELECT username FROM users WHERE user_id = %s",
                (user_id,)
            )
            result = cursor.fetchone()
            return result[0] if result else None
    except (Exception, pg.DatabaseError) as error:
        logger.error(f"[-] {error}")
        return None


def is_maintenance_mode() -> bool:
    """Проверить режим технических работ"""
    return get_setting('maintenance_mode') == '1'
