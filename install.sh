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
echo -e "${YELLOW}[1/8] Обновление пакетов...${NC}"
apt update && apt upgrade -y

# Установка зависимостей
echo -e "${YELLOW}[2/8] Установка зависимостей...${NC}"
apt install -y git python3-pip python3-venv postgresql postgresql-contrib curl wget qrencode sudo

# Установка Amnezia WireGuard
echo -e "${YELLOW}[3/8] Установка Amnezia WireGuard...${NC}"
cd /tmp
git clone https://github.com/amnezia-vpn/amneziawg-tools.git
cd amneziawg-tools
./configure
make
make install
modprobe amneziawg
cd ..
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
echo -e "${YELLOW}[5/8] Копирование файлов бота...${NC}"
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
echo -e "${YELLOW}[6/8] Настройка Python окружения...${NC}"
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# Генерация .env файла
echo -e "${YELLOW}[7/8] Генерация конфигурации .env...${NC}"
BOT_TOKEN=""
ADMIN_ID=""
GROUP_LINK=""

read -p "Введите токен бота (@BotFather): " BOT_TOKEN
read -p "Введите ваш Telegram ID (администратор): " ADMIN_ID
read -p "Введите ссылку на обязательную группу (например, https://t.me/mychannel): " GROUP_LINK

# Сохранение .env
cat > .env <<EOF
BOT_TOKEN=$BOT_TOKEN
ADMINS=$ADMIN_ID
DATABASE_URL=postgresql+asyncpg://$DB_USER:$DB_PASS@localhost/$DB_NAME
GROUP_LINK=$GROUP_LINK
PAYMENT_METHOD=manual
CRYPTOBOT_TOKEN=
AMNEZIA_JC=6
AMNEZIA_JMIN=350
AMNEZIA_JMAX=900
AMNEZIA_S1=15
AMNEZIA_S2=150
AMNEZIA_H1=18446744073709551615
AMNEZIA_H2=18446744073709551615
AMNEZIA_H3=18446744073709551615
AMNEZIA_H4=18446744073709551615
EOF

chmod 600 .env

# Настройка systemd сервиса
echo -e "${YELLOW}[8/8] Создание сервиса...${NC}"
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
