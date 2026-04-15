<h1 align="center">Amnezia WireGuard Bot - Простой VPN бот для Telegram</h1>
<p align="center">
<img src = "image/logo_wide.png" width = 50%>
</p>

<div align="center">

[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Packaged with Poetry](https://img.shields.io/badge/packaging-poetry-cyan.svg)](https://python-poetry.org/)
<br>
[![!Ubuntu](https://img.shields.io/badge/Ubuntu-E95420?style=for-the-badge&logo=ubuntu&logoColor=white)](https://ubuntu.com/)
[![!Debian](https://img.shields.io/badge/Debian-A81D33?style=for-the-badge&logo=debian&logoColor=white)](https://www.debian.org/)
[![!Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![!PostgreSQL](https://img.shields.io/badge/PostgreSQL-4169E1?style=for-the-badge&logo=postgresql&logoColor=white)](https://www.postgresql.org/)
[![!AmneziaWG](https://img.shields.io/badge/AmneziaWG-88171A?style=for-the-badge&logo=wireguard&logoColor=white)](https://amnezia.org/)
[![!Telegram](https://img.shields.io/badge/Telegram-2CA5E0?style=for-the-badge&logo=telegram&logoColor=white)](https://telegram.org/)

</div>

## Описание

Надежный и простой бот для управления Amnezia WireGuard VPN сервером. Предназначен для продажи доступа к VPN через Telegram с автоматизацией выдачи конфигов и контролем подписок.

### Ключевые функции:

- **Amnezia WireGuard Support**: Использует протокол AmneziaWG с встроенной обфускацией для обхода блокировок
- **Автоматическое управление подписками**: Пользователи получают уведомления за 3 дня, 2 дня, 1 день до окончания подписки
- **Пробный период**: Новые пользователи автоматически получают 1 день бесплатного доступа
- **Реферальная система**: Пригласите друга и получите по 10 дней бонуса при оплате им подписки
- **Проверка подписки на группу**: Опциональная возможность требовать подписку на Telegram канал
- **Авто-отключение**: Пользователи автоматически отключаются при истечении подписки
- **Генерация QR-кодов**: Мобильные QR-коды для быстрой настройки VPN (совместимо с AmneziaVPN)
- **Панель администратора**: Полный контроль над пользователями, подписками и конфигами
- **Простая оплата**: Оплата через скриншот платежа - никаких сложных интеграций

## Стек технологий

- **Язык**: Python 3.10+
- **Фреймворк**: aiogram 3.x
- **База данных**: PostgreSQL
- **VPN протокол**: Amnezia WireGuard (с обфускацией)
- **Контейнеризация**: Docker & Docker Compose

## Быстрый старт

### Вариант 1: Автоматическая установка на один сервер (рекомендуется)

Скрипт автоматически установит Amnezia WireGuard, PostgreSQL и настроит бота на одном VPS. Вам нужно будет ввести только токен бота и данные для подключения:

```bash
wget https://raw.githubusercontent.com/wireguard-bot/master/install.sh && chmod +x install.sh && sudo ./install.sh
```

**В процессе установки вам потребуется ввести:**

1. **Данные Amnezia WireGuard**:
   - Использовать этот же сервер? (да/нет) - по умолчанию "да"
   - Пароль root для SSH доступа
   - Имя сервиса WireGuard (по умолчанию "wireguard")

2. **Данные Telegram бота**:
   - Токен бота от @BotFather
   - Ваш Telegram ID (администратор)
   - Ссылка на группу (опционально)
   - Цена подписки в месяц (по умолчанию 199 руб)
   - Номер карты для оплаты (опционально)

Скрипт автоматически:
- Установит все зависимости
- Настроит Amnezia WireGuard
- Создаст базу данных PostgreSQL
- Сгенерирует ключи WireGuard
- Настроит автозапуск бота

### Вариант 2: Ручная установка через Docker

1. Клонируйте репозиторий:
```bash
git clone https://github.com/wireguard-bot.git && cd wireguard-bot
```

2. Создайте файл `.env` в корне проекта:
```bash
cp data/.env.sample .env
nano .env
```

3. Заполните `.env` своими данными:
```ini
# TELEGRAM SETTINGS
# Токен Telegram бота (получить у @BotFather)
BOT_TOKEN=your_bot_token_here

# ID администраторов (можно несколько через запятую)
ADMINS=123456789

# AMNEZIA WIREGUARD SETTINGS
# Данные для подключения к серверу Amnezia (если бот и VPN на одном сервере - 127.0.0.1)
AMNEZIA_HOST=127.0.0.1
AMNEZIA_PORT=22
AMNEZIA_USER=root
AMNEZIA_PASSWORD=your_root_password
AMNEZIA_SERVICE_NAME=wireguard

# VPN SETTINGS (Amnezia WireGuard)
# Префикс для имен конфигов
CONFIGS_PREFIX=myvpn

# DNS сервер (по умолчанию 8.8.8.8)
PEER_DNS=8.8.8.8

# PAYMENT SETTINGS
# Номер карты для оплаты
PAYMENT_CARD=0000 0000 0000 0000

# Цена подписки в рублях
BASE_SUBSCRIPTION_MONTHLY_PRICE_RUBLES=299

# DATABASE SETTINGS
DB_HOST=localhost
DB_PORT=5432
DB_USER=vpnuser
DB_USER_PASSWORD=vpnpass
DATABASE=vpnbot

# GROUP SETTINGS (опционально)
# ID группы, обязательной для подписки
REQUIRED_GROUP_ID=-1001234567890

# ADVANCED
TRIAL_DAYS=1
REFERRAL_BONUS_DAYS=10
```

4. Запустите через Docker Compose:
```bash
docker-compose up -d
```

5. Инициализируйте базу данных:
```bash
docker-compose exec vpnbot python database/create.py
```

## Административные команды

- `/give <user_id> <days>` - Продлить подписку пользователю на указанное количество дней
- `/stats` - Показать статистику пользователей
- `/wgrestart` - Перезагрузить сервис WireGuard
- `/broadcast` - Создать рассылку пользователям
- `/tickets` - Просмотреть обращения в поддержку

## Реферальная система

Каждый пользователь получает уникальную реферальную ссылку вида:
`https://t.me/<bot_username>?start=<user_id>`

Когда приглашенный друг оплачивает подписку:
- Приглашенный получает +10 дней к подписке
- Пригласивший получает +10 дней бонуса

## Клиентские приложения

Для подключения к VPN пользователям необходимо установить клиент AmneziaVPN:

- **Android**: [Google Play](https://play.google.com/store/apps/details?id=org.amnezia.awg&hl=ru)
- **iOS**: [App Store](https://apps.apple.com/ru/app/amneziawg/id6478942365)

Конфигурационные файлы `.conf` выдаются автоматически при создании подписки. Также генерируются QR-коды для быстрой настройки на мобильных устройствах.

## Структура проекта

```
├── app.py                 # Точка входа приложения
├── handlers/              # Обработчики команд
│   ├── user.py           # Пользовательские команды
│   ├── admin.py          # Административные команды
│   └── admin_extended.py # Расширенные функции админа
├── keyboards/             # Клавиатуры для бота
├── database/              # Работа с базой данных
├── utils/                 # Вспомогательные функции
├── data/                  # Конфигурация и данные
├── docker-compose.yml     # Docker конфигурация
└── README.md             # Документация
```

## Поддержка

В случае возникновения вопросов или проблем:
- Напишите в техническую поддержку через бота (команда `/support`)
- Свяжитесь с администратором напрямую

## Лицензия

MIT License

---

**Amnezia WireGuard Bot** - надежное решение для продажи VPN доступа ❤️
