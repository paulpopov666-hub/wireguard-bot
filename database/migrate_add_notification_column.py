# Migration script to add last_notification_sent column to users table
import psycopg2 as pg
from loguru import logger
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv('/workspace/data/.env')

def get_db_connection_params():
    """Get database connection parameters from environment variables"""
    return {
        'dbname': os.getenv('DATABASE'),
        'user': os.getenv('DB_USER'),
        'password': os.getenv('DB_USER_PASSWORD'),
        'host': os.getenv('DB_HOST', 'localhost'),
        'port': os.getenv('DB_PORT', '5432')
    }


def add_last_notification_sent_column() -> None:
    """Add last_notification_sent column to users table if it doesn't exist"""
    try:
        conn_params = get_db_connection_params()
        conn = pg.connect(**conn_params)
        with conn.cursor() as cursor:
            # Check if column exists
            cursor.execute(
                """--sql
                SELECT EXISTS (
                    SELECT 1 FROM information_schema.columns 
                    WHERE table_name = 'users' AND column_name = 'last_notification_sent'
                )
                """
            )
            column_exists = cursor.fetchone()[0]
            
            if not column_exists:
                cursor.execute(
                    """--sql
                    ALTER TABLE users ADD COLUMN last_notification_sent TIMESTAMP DEFAULT NULL
                    """
                )
                conn.commit()
                logger.success("[+] Column last_notification_sent added to users table")
            else:
                logger.info("[+] Column last_notification_sent already exists in users table")
                
    except (Exception, pg.DatabaseError) as error:
        logger.error(f"[-] {error}")


if __name__ == "__main__":
    add_last_notification_sent_column()
