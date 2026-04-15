#!/bin/bash

# Amnezia WireGuard VPN Bot - Semi-Automatic Installation Script
# This script installs and configures the VPN bot with Amnezia WireGuard

set -e

echo "=========================================="
echo "  Amnezia WireGuard VPN Bot Installer"
echo "=========================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored messages
print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_info() {
    echo -e "${YELLOW}→ $1${NC}"
}

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
    print_error "Please run as root (use sudo)"
    exit 1
fi

print_info "Updating system packages..."
apt-get update -qq

print_info "Installing dependencies..."
apt-get install -y -qq \
    python3 \
    python3-pip \
    python3-venv \
    git \
    curl \
    wget \
    jq \
    postgresql \
    postgresql-contrib \
    systemd \
    >> /dev/null 2>&1

print_success "System dependencies installed"

# Install Amnezia WireGuard tools
print_info "Installing Amnezia WireGuard tools..."
if ! command -v amneziawg &> /dev/null; then
    apt-get install -y -qq software-properties-common apt-transport-https >> /dev/null 2>&1
    
    # Download and install amneziawg-tools from GitHub releases
    TEMP_DIR=$(mktemp -d)
    cd "$TEMP_DIR"
    
    # Get latest release version
    LATEST_VERSION=$(curl -s https://api.github.com/repos/amnezia-vpn/amneziawg-tools/releases/latest | jq -r .tag_name | sed 's/v//')
    
    # Download deb package
    wget -q "https://github.com/amnezia-vpn/amneziawg-tools/releases/download/v${LATEST_VERSION}/amneziawg-tools_${LATEST_VERSION}_amd64.deb"
    
    # Install
    dpkg -i "amneziawg-tools_${LATEST_VERSION}_amd64.deb" >> /dev/null 2>&1
    
    cd - > /dev/null
    rm -rf "$TEMP_DIR"
    
    print_success "Amnezia WireGuard tools installed (version ${LATEST_VERSION})"
else
    print_success "Amnezia WireGuard tools already installed"
fi

# Setup PostgreSQL
print_info "Configuring PostgreSQL..."
systemctl enable postgresql >> /dev/null 2>&1
systemctl start postgresql >> /dev/null 2>&1

# Create database and user
sudo -u postgres psql -c "CREATE DATABASE vpnbot;" >> /dev/null 2>&1 || true
sudo -u postgres psql -c "CREATE USER vpnuser WITH PASSWORD 'vpnpassword123';" >> /dev/null 2>&1 || true
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE vpnbot TO vpnuser;" >> /dev/null 2>&1

print_success "PostgreSQL configured"

# Create bot directory
BOT_DIR="/opt/vpnbot"
print_info "Creating bot directory at $BOT_DIR..."
mkdir -p "$BOT_DIR"
cd "$BOT_DIR"

# Clone or update repository
if [ -d ".git" ]; then
    print_info "Updating existing installation..."
    git pull --quiet
else
    print_info "Cloning repository..."
    git clone https://github.com/PheeZz/wireguard-bot.git . --quiet
fi

print_success "Bot code ready"

# Create virtual environment
print_info "Setting up Python virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Install Python dependencies
print_info "Installing Python dependencies..."
pip install --upgrade pip --quiet
pip install -r requirements.txt --quiet

print_success "Python dependencies installed"

# Generate .env file
print_info "Generating configuration file..."
cat > .env << EOF
# Bot Configuration
BOT_TOKEN=YOUR_BOT_TOKEN_HERE
ADMINS=YOUR_TELEGRAM_ID_HERE

# Payment Configuration
# Choose payment method: 'manual' (screenshots) or 'cryptobot'
PAYMENT_METHOD=manual
PAYMENT_CARD=2200000000000000
CRYPTOBOT_TOKEN=

# Pricing
BASE_SUBSCRIPTION_MONTHLY_PRICE_RUBLES=299

# Database Configuration
DB_HOST=localhost
DB_PORT=5432
DB_USER=vpnuser
DB_USER_PASSWORD=vpnpassword123
DATABASE=vpnbot

# WireGuard Configuration
CONFIGS_PREFIX=wg_config
PEER_DNS=8.8.8.8

# Required Telegram Group ID (optional, for membership check)
REQUIRED_GROUP_ID=

# AmneziaWG Obfuscation Parameters
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

print_success "Configuration file created at $BOT_DIR/.env"

# Run database migration
print_info "Running database migration..."
python database/migrate_v2.py

print_success "Database migration completed"

# Create systemd service
print_info "Creating systemd service..."
cat > /etc/systemd/system/vpnbot.service << EOF
[Unit]
Description=Amnezia WireGuard VPN Bot
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
systemctl enable vpnbot >> /dev/null 2>&1

print_success "Systemd service created"

# Configure firewall
print_info "Configuring firewall..."
if command -v ufw &> /dev/null; then
    ufw allow 51820/udp >> /dev/null 2>&1 || true
    print_success "Firewall configured (UDP port 51820 allowed)"
else
    print_info "UFW not installed, skipping firewall configuration"
fi

# Enable IP forwarding
print_info "Enabling IP forwarding..."
echo "net.ipv4.ip_forward=1" >> /etc/sysctl.conf
sysctl -p >> /dev/null 2>&1

print_success "IP forwarding enabled"

# Final instructions
echo ""
echo "=========================================="
echo -e "${GREEN}Installation completed successfully!${NC}"
echo "=========================================="
echo ""
echo "IMPORTANT: Before starting the bot, you must:"
echo ""
echo "1. Edit the configuration file:"
echo "   nano $BOT_DIR/.env"
echo ""
echo "   Replace these values:"
echo "   - BOT_TOKEN: Get from @BotFather in Telegram"
echo "   - ADMINS: Your Telegram user ID (get from @userinfobot)"
echo "   - REQUIRED_GROUP_ID: Your Telegram group ID (optional)"
echo "   - CRYPTOBOT_TOKEN: If using CryptoBot payments (optional)"
echo ""
echo "2. Start the bot:"
echo "   systemctl start vpnbot"
echo ""
echo "3. Check bot status:"
echo "   systemctl status vpnbot"
echo ""
echo "4. View logs:"
echo "   journalctl -u vpnbot -f"
echo ""
echo "=========================================="
echo ""

# Ask to start the bot
read -p "Do you want to start the bot now? (y/n): " -n 1 -r
echo ""
if [[ $REPLY =~ ^[Yy]$ ]]; then
    systemctl start vpnbot
    print_success "Bot started!"
    print_info "Check status with: systemctl status vpnbot"
fi
