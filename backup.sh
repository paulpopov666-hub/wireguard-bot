#!/bin/bash
# Автоматическое резервное копирование БД и конфигов

BACKUP_DIR="/app/backups"
DATE=$(date +%Y-%m-%d_%H-%M)
DB_NAME="${DB_NAME:-vpnbot}"
DB_USER="${DB_USER:-vpnuser}"

mkdir -p $BACKUP_DIR

# Backup database
pg_dump -h localhost -U $DB_USER $DB_NAME > $BACKUP_DIR/db_$DATE.sql

# Backup wireguard configs
tar -czf $BACKUP_DIR/wireguard_$DATE.tar.gz /etc/wireguard/

# Backup .env
cp .env $BACKUP_DIR/env_$DATE

# Delete backups older than 7 days
find $BACKUP_DIR -type f -mtime +7 -delete

echo "Backup completed: $DATE"
