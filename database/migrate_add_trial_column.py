import psycopg2 as pg
from loguru import logger
from data import configuration


def migrate_add_trial_column() -> None:
    """Add trial_used column to users table if not exists"""
    try:
        conn = pg.connect(**configuration.db_connection_parameters)
        with conn.cursor() as cursor:
            # Check if column exists
            cursor.execute("""
                SELECT EXISTS (
                    SELECT 1 FROM information_schema.columns 
                    WHERE table_name = 'users' AND column_name = 'trial_used'
                )
            """)
            column_exists = cursor.fetchone()[0]
            
            if not column_exists:
                cursor.execute("""
                    ALTER TABLE users ADD COLUMN trial_used BOOLEAN DEFAULT FALSE
                """)
                conn.commit()
                logger.success("[+] Column trial_used added to users table")
            else:
                logger.info("[+] Column trial_used already exists in users table")
    except (Exception, pg.DatabaseError) as error:
        logger.error(f"[-] {error}")


if __name__ == "__main__":
    migrate_add_trial_column()
