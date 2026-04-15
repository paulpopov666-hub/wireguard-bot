#!/bin/bash

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}=========================================${NC}"
echo -e "${GREEN}  Установка VPN Bot с Amnezia WireGuard ${NC}"
echo -e "${GREEN}=========================================${NC}"

# Проверка root прав
if [ "$EUID" -ne 0 ]; then 
  echo -e "${RED}Ошибка: Запускайте скрипт от root (sudo su)${NC}"
  exit 1
fi

# Обновление системы
echo -e "${YELLOW}[1/9] Обновление пакетов...${NC}"
apt update && apt upgrade -y

# Установка зависимостей
echo -e "${YELLOW}[2/9] Установка зависимостей...${NC}"
apt install -y git python3-pip python3-venv postgresql postgresql-contrib curl wget qrencode sudo \
    build-essential libtool pkg-config autoconf automake dkms linux-headers-$(uname -r) \
    qtbase5-dev qtchooser qt5-qmake qtbase5-dev-tools

# Установка Amnezia WireGuard (исправленная версия)
echo -e "${YELLOW}[3/9] Установка Amnezia WireGuard...${NC}"
cd /tmp
rm -rf amneziawg-tools
git clone https://github.com/amnezia-vpn/amneziawg-tools.git
cd amneziawg-tools

# Проверяем наличие разных методов сборки
if [ -f "autogen.sh" ]; then
    echo "   Используем autogen.sh..."
    ./autogen.sh
    ./configure
    make
    make install
elif [ -f "CMakeLists.txt" ]; then
    echo "   Используем CMake..."
    mkdir build && cd build
    cmake ..
    make
    make install
    cd ..
else
    # Для версий без autogen.sh используем qmake
    echo "   Используем qmake..."
    qmake
    make
    make install
fi

modprobe amneziawg || echo "⚠️ Модуль не загрузился сразу, потребуется перезагрузка"
cd /tmp
rm -rf amneziawg-tools

# Настройка PostgreSQL
echo -e "${YELLOW}[4/8] Настройка базы данных...${NC}"
systemctl enable postgresql
systemctl start postgresql

DB_USER="vpnbot"
DB_PASS=$(openssl rand -base64 12)
DB_NAME="vpnbot_db"

su - postgres -c "psql -c \"CREATE USER $DB_USER WITH PASSWORD '$DB_PASS';\""
su - postgres -c "psql -c \"CREATE DATABASE $DB_NAME OWNER $DB_USER;\""
su - postgres -c "psql -c \"GRANT ALL PRIVILEGES ON DATABASE $DB_NAME TO $DB_USER;\""

echo -e "${GREEN}База данных создана:${NC}"
echo "User: $DB_USER"
echo "Pass: $DB_PASS"
echo "DB:   $DB_NAME"

# Подготовка директории бота
echo -e "${YELLOW}[5/9] Копирование файлов бота...${NC}"
BOT_DIR="/opt/vpnbot"
mkdir -p $BOT_DIR

# Копируем текущие файлы из рабочей директории (предполагается, что скрипт запущен из папки с проектом или они уже тут)
# Если вы запускаете этот скрипт отдельно, убедитесь, что файлы проекта доступны.
# Для удобства, если скрипт лежит в корне проекта:
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
if [ -f "$SCRIPT_DIR/app.py" ]; then
    cp -r "$SCRIPT_DIR"/* $BOT_DIR/
else
    echo -e "${RED}Ошибка: Файлы бота не найдены в текущей директории.${NC}"
    echo "Убедитесь, что запускаете install.sh из папки с проектом."
    exit 1
fi

cd $BOT_DIR

# Создание виртуального окружения
echo -e "${YELLOW}[6/9] Настройка Python окружения...${NC}"
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# Генерация .env файла с автоматическим определением параметров
echo -e "${YELLOW}[7/9] Генерация конфигурации .env...${NC}"

# Автоматическое определение IP сервера
SERVER_IP=$(curl -s ifconfig.me || curl -s ipinfo.io/ip || hostname -I | awk '{print $1}')
echo "   🌍 Обнаружен IP сервера: $SERVER_IP"

# Генерация ключей WireGuard
WG_PRIV=$(awg genkey 2>/dev/null || wg genkey)
WG_PUB=$(echo "$WG_PRIV" | awg pubkey 2>/dev/null || echo "$WG_PRIV" | wg pubkey)
WG_PSK=$(awg genpsk 2>/dev/null || wg genpsk)
echo "   🔑 Ключи WireGuard сгенерированы"

# Генерация пароля для БД
DB_PASS_GEN=$(openssl rand -base64 16 | tr -dc 'a-zA-Z0-9' | head -c 20)
echo "   🔒 Пароль БД сгенерирован"

# Запрос данных у пользователя
BOT_TOKEN=""
ADMIN_ID=""
GROUP_LINK=""
PRICE="199"
CARD=""

# Данные для подключения к серверу Amnezia (автоматически для локальной установки)
echo ""
echo -e "${YELLOW}=== НАСТРОЙКА AMNEZIA WIREGUARD ===${NC}"
echo -e "${GREEN}Поскольку бот и VPN устанавливаются на один сервер, настройка сети будет выполнена автоматически.${NC}"

# Используем локальный сервер автоматически
AMNEZIA_HOST="127.0.0.1"
AMNEZIA_PORT="22"
AMNEZIA_USER="root"

# Для локального подключения пароль не требуется при использовании SSH ключей или localhost без проверки,
# но для унификации конфигурации бота запишем пустое значение или заглушку, 
# так как бот может использовать прямое обращение к конфигам, а не SSH.
# Если бот все же требует поле password, оставим его пустым или поставим заглушку.
AMNEZIA_PASSWORD="" 

AMNEZIA_SERVICE_NAME="wireguard"

echo -e "   🌍 Хост: ${AMNEZIA_HOST} (локально)"
echo -e "   🔌 Порт SSH: ${AMNEZIA_PORT}"
echo -e "   👤 Пользователь: ${AMNEZIA_USER}"
echo -e "   📦 Сервис: ${AMNEZIA_SERVICE_NAME}"

echo ""
echo -e "${YELLOW}=== НАСТРОЙКА TELEGRAM БОТА ===${NC}"
read -p "Введите токен бота (@BotFather): " BOT_TOKEN
read -p "Введите ваш Telegram ID (администратор): " ADMIN_ID
read -p "Введите ссылку на обязательную группу (например, https://t.me/mychannel, можно пропустить): " GROUP_LINK
read -p "Цена подписки в месяц (руб, по умолчанию 199): " PRICE_INPUT
if [ -n "$PRICE_INPUT" ]; then
    PRICE=$PRICE_INPUT
fi
read -p "Номер карты для оплаты (необязательно): " CARD_INPUT
if [ -n "$CARD_INPUT" ]; then
    CARD=$CARD_INPUT
fi

# Сохранение .env
cat > .env <<EOF
# TELEGRAM SETTINGS
BOT_TOKEN=$BOT_TOKEN
ADMINS=$ADMIN_ID

# AMNEZIA WIREGUARD SETTINGS
AMNEZIA_HOST=$AMNEZIA_HOST
AMNEZIA_PORT=$AMNEZIA_PORT
AMNEZIA_USER=$AMNEZIA_USER
AMNEZIA_PASSWORD=$AMNEZIA_PASSWORD
AMNEZIA_SERVICE_NAME=$AMNEZIA_SERVICE_NAME

# VPN SETTINGS (Amnezia WireGuard)
WG_SERVER_IP=$SERVER_IP
WG_SERVER_PORT=51820
WG_SERVER_PUBLIC_KEY=$WG_PUB
WG_SERVER_PRESHARED_KEY=$WG_PSK
WG_CFG_PATH=/etc/amnezia/amneziawg/wg0.conf
CONFIGS_PREFIX=AMNEZIA_VPN
PEER_DNS=1.1.1.1

# PAYMENT SETTINGS
PAYMENT_METHOD=manual
PAYMENT_CARD=$CARD
BASE_SUBSCRIPTION_MONTHLY_PRICE_RUBLES=$PRICE

# GROUP SETTINGS
GROUP_LINK=$GROUP_LINK

# DATABASE SETTINGS
DB_HOST=localhost
DB_PORT=5432
DB_USER=$DB_USER
DB_USER_PASSWORD=$DB_PASS_GEN
DATABASE=$DB_NAME

# ADVANCED
TRIAL_DAYS=1
REFERRAL_BONUS_DAYS=10
OBFUSCATION_JC=10
OBFUSCATION_JMIN=5
OBFUSCATION_JMAX=20
OBFUSCATION_S1=30
OBFUSCATION_S2=40
OBFUSCATION_H1=1
OBFUSCATION_H2=2
OBFUSCATION_H3=3
OBFUSCATION_H4=4
EOF

chmod 600 .env
echo "   ✅ Файл .env создан"

# Настройка конфига WireGuard сервера
echo -e "${YELLOW}[8/9] Настройка WireGuard сервера...${NC}"
WG_CONFIG_DIR="/etc/amnezia/amneziawg"
mkdir -p $WG_CONFIG_DIR

# Определяем сетевой интерфейс
INTERFACE=$(ip route | grep default | awk '{print $5}' | head -n1)
if [ -z "$INTERFACE" ]; then
    INTERFACE="eth0"
fi

cat > $WG_CONFIG_DIR/wg0.conf <<EOF
[Interface]
Address = 10.0.0.1/24
ListenPort = 51820
PrivateKey = $WG_PRIV
PostUp = iptables -A FORWARD -i %i -j ACCEPT; iptables -A FORWARD -o %i -j ACCEPT; iptables -t nat -A POSTROUTING -o $INTERFACE -j MASQUERADE
PostDown = iptables -D FORWARD -i %i -j ACCEPT; iptables -D FORWARD -o %i -j ACCEPT; iptables -t nat -D POSTROUTING -o $INTERFACE -j MASQUERADE
SaveConfig = false
EOF

# Поднимаем интерфейс
awg-quick up wg0 2>/dev/null || wg-quick up wg0 2>/dev/null || echo "⚠️ Интерфейс не поднят (возможно после перезагрузки)"
systemctl enable awg-quick@wg0 2>/dev/null || systemctl enable wg-quick@wg0 2>/dev/null || true
echo "   ✅ WireGuard настроен"

# Выполнение миграции БД
echo "   Выполнение миграции базы данных..."
source venv/bin/activate
python database/migrate_v2.py 2>/dev/null || echo "⚠️ Миграция не выполнена (будет при первом запуске)"

# Настройка systemd сервиса
echo -e "${YELLOW}[9/9] Создание сервиса...${NC}"
cat > /etc/systemd/system/vpnbot.service <<EOF
[Unit]
Description=VPN Bot with Amnezia WireGuard
After=network.target postgresql.service

[Service]
Type=simple
User=root
WorkingDirectory=$BOT_DIR
Environment="PATH=$BOT_DIR/venv/bin"
ExecStart=$BOT_DIR/venv/bin/python app.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable vpnbot

# Настройка Firewall
echo -e "${YELLOW}Настройка Firewall...${NC}"
ufw allow 51820/udp || true # Порт WG
ufw allow ssh || true
ufw --force enable || true

# Запуск
echo -e "${GREEN}Запуск бота...${NC}"
systemctl start vpnbot

echo ""
echo -e "${GREEN}=========================================${NC}"
echo -e "${GREEN}  УСПЕШНО УСТАНОВЛЕНО! ${NC}"
echo -e "${GREEN}=========================================${NC}"
echo -e "Статус бота: ${GREEN}$(systemctl is-active vpnbot)${NC}"
echo -e "Логи: ${YELLOW}journalctl -u vpnbot -f${NC}"
echo -e "Папка установки: ${YELLOW}$BOT_DIR${NC}"
echo ""
echo -e "${RED}ВАЖНО: Не забудьте добавить бота администратором в группу!${NC}"
echo -e "Ссылка на группу: $GROUP_LINK"
