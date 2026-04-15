"""Migration script to add referral system columns to users table"""
import psycopg2 as pg
from loguru import logger
from data import configuration


def migrate_add_referral_columns() -> None:
    """Add referred_by and referral_bonus_days columns to users table"""
    try:
        conn = pg.connect(**configuration.db_connection_parameters)
        with conn.cursor() as cursor:
            # Add referred_by column
            cursor.execute("""
                ALTER TABLE users 
                ADD COLUMN IF NOT EXISTS referred_by BIGINT DEFAULT NULL
            """)
            
            # Add referral_bonus_days column
            cursor.execute("""
                ALTER TABLE users 
                ADD COLUMN IF NOT EXISTS referral_bonus_days INT DEFAULT 0
            """)
            
            # Add foreign key constraint if not exists
            cursor.execute("""
                DO $$
                BEGIN
                    IF NOT EXISTS (
                        SELECT 1 FROM information_schema.table_constraints 
                        WHERE constraint_name = 'users_referred_by_fkey'
                    ) THEN
                        ALTER TABLE users 
                        ADD CONSTRAINT users_referred_by_fkey 
                        FOREIGN KEY (referred_by) REFERENCES users (user_id);
                    END IF;
                END $$
            """)
            
            conn.commit()
            logger.success("[+] Referral columns added successfully")
    except (Exception, pg.DatabaseError) as error:
        logger.error(f"[-] Migration error: {error}")


if __name__ == "__main__":
    migrate_add_referral_columns()
