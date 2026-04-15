import sqlite3
import os
from datetime import datetime

DB_PATH = "data/users.db"

def migrate():
    if not os.path.exists(DB_PATH):
        print("База данных не найдена. Создаем новую...")
        # Если БД нет, создадим структуру с нуля (упрощенно, полная структура в models.py)
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        # Создаем таблицу пользователей (базовая)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                first_name TEXT,
                subscription_end_date TEXT,
                trial_used INTEGER DEFAULT 0,
                referral_code TEXT,
                referred_by INTEGER,
                balance_days INTEGER DEFAULT 0,
                configs_count INTEGER DEFAULT 1,
                language TEXT DEFAULT 'ru',
                joined_group INTEGER DEFAULT 0,
                last_check_date TEXT,
                notification_sent_3d INTEGER DEFAULT 0,
                notification_sent_2d INTEGER DEFAULT 0,
                notification_sent_1d INTEGER DEFAULT 0,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        # Таблица платежей
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS payments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                amount REAL,
                currency TEXT,
                status TEXT,
                proof_photo_id TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(user_id) REFERENCES users(user_id)
            )
        """)
        # Таблица тикетов (новая)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS tickets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                message_text TEXT,
                status TEXT DEFAULT 'open',
                admin_reply TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                closed_at TEXT,
                FOREIGN KEY(user_id) REFERENCES users(user_id)
            )
        """)
        # Таблица промокодов (новая)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS promo_codes (
                code TEXT PRIMARY KEY,
                bonus_days INTEGER,
                usage_count INTEGER DEFAULT 0,
                max_usages INTEGER DEFAULT 0,
                is_active INTEGER DEFAULT 1
            )
        """)
        # Таблица настроек бота (новая)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS settings (
                key TEXT PRIMARY KEY,
                value TEXT
            )
        """)
        
        # Добавляем дефолтные настройки
        cursor.execute("INSERT OR IGNORE INTO settings (key, value) VALUES ('maintenance_mode', '0')")
        cursor.execute("INSERT OR IGNORE INTO settings (key, value) VALUES ('obfuscation_params', '{\"Jc\": 5, \"Jmin\": 50, \"Jmax\": 100, \"S1\": 20, \"S2\": 40, \"H1\": \"hello\", \"H2\": \"world\", \"H3\": \"test\", \"H4\": \"data\"}')")
        
        conn.commit()
        conn.close()
        print("Базовая структура создана.")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    try:
        # 1. Добавляем поле для языка, если нет
        cursor.execute("ALTER TABLE users ADD COLUMN language TEXT DEFAULT 'ru'")
        print("Добавлено поле language")
    except sqlite3.OperationalError:
        pass # Поле уже есть

    try:
        # 2. Добавляем поле количества конфигов
        cursor.execute("ALTER TABLE users ADD COLUMN configs_count INTEGER DEFAULT 1")
        print("Добавлено поле configs_count")
    except sqlite3.OperationalError:
        pass

    try:
        # 3. Добавляем поле последнего проверки группы
        cursor.execute("ALTER TABLE users ADD COLUMN last_check_date TEXT")
        print("Добавлено поле last_check_date")
    except sqlite3.OperationalError:
        pass

    # 4. Создаем таблицу тикетов, если нет
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tickets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            message_text TEXT,
            status TEXT DEFAULT 'open',
            admin_reply TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            closed_at TEXT
        )
    """)
    print("Таблица tickets проверена/создана")

    # 5. Создаем таблицу промокодов
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS promo_codes (
            code TEXT PRIMARY KEY,
            bonus_days INTEGER,
            usage_count INTEGER DEFAULT 0,
            max_usages INTEGER DEFAULT 0,
            is_active INTEGER DEFAULT 1
        )
    """)
    print("Таблица promo_codes проверена/создана")

    # 6. Создаем таблицу настроек
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS settings (
            key TEXT PRIMARY KEY,
            value TEXT
        )
    """)
    
    # Инициализация дефолтных значений
    cursor.execute("INSERT OR IGNORE INTO settings (key, value) VALUES ('maintenance_mode', '0')")
    cursor.execute("INSERT OR IGNORE INTO settings (key, value) VALUES ('obfuscation_params', '{\"Jc\": 5, \"Jmin\": 50, \"Jmax\": 100, \"S1\": 20, \"S2\": 40, \"H1\": \"hello\", \"H2\": \"world\", \"H3\": \"test\", \"H4\": \"data\"}')")
    print("Таблица settings проверена/создана и инициализирована")

    conn.commit()
    conn.close()
    print("Миграция успешно завершена!")

if __name__ == "__main__":
    migrate()
