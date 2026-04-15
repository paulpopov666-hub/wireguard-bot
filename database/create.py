import psycopg2 as pg
from loguru import logger
from data import configuration



def create_table_user() -> None:
    """Create table user in database wireguard_bot
    Default value for subscription_end_date is 999 days ago
    last_notification_sent stores timestamp of last reminder notification
    trial_used stores whether user has already used trial period
    referred_by stores user_id of the referrer (who invited this user)
    referral_bonus_days stores total bonus days earned from referrals
    """
    try:
        conn = pg.connect(**configuration.db_connection_parameters)
        with conn.cursor() as cursor:
            cursor.execute(
                """--sql
                CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                user_id BIGINT UNIQUE,
                username VARCHAR(255) UNIQUE,
                is_admin BOOLEAN DEFAULT FALSE,
                is_banned BOOLEAN DEFAULT FALSE,
                subscription_end_date TIMESTAMP DEFAULT now() - interval '999 days',
                config_count INT DEFAULT 0,
                last_notification_sent TIMESTAMP DEFAULT NULL,
                trial_used BOOLEAN DEFAULT FALSE,
                referred_by BIGINT DEFAULT NULL,
                referral_bonus_days INT DEFAULT 0,
                FOREIGN KEY (referred_by) REFERENCES users (user_id));
                """
            )
            conn.commit()
            logger.success("[+] Table user created successfully")
    except (Exception, pg.DatabaseError) as error:
        logger.error(f"[-] {error}")


def create_table_vpn_config() -> None:
    """Create table vpn_config in database wireguard_bot"""
    try:
        conn = pg.connect(**configuration.db_connection_parameters)

        with conn.cursor() as cursor:
            cursor.execute(
                """--sql
                CREATE TABLE IF NOT EXISTS vpn_config (
                id SERIAL PRIMARY KEY,
                user_id BIGINT,
                config_name VARCHAR(255),
                config TEXT,
                FOREIGN KEY (user_id) REFERENCES users (user_id))
                """
            )
            conn.commit()
            logger.success("[+] Table vpn_config created successfully")
    except (Exception, pg.DatabaseError) as error:
        logger.error(f"[-] {error}")


if __name__ == "__main__":
    create_table_user()
    create_table_vpn_config()
