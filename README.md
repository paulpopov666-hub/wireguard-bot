<h1 align="center">Amnezia WireGuard Bot - VPN Management with Referral System</h1>
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
[![!AdGuard](https://img.shields.io/badge/AdGuard-00A6D6?style=for-the-badge&logo=adguard&logoColor=white)](https://adguard.com/)
[![!Telegram](https://img.shields.io/badge/Telegram-2CA5E0?style=for-the-badge&logo=telegram&logoColor=white)](https://telegram.org/)

</div>

## Contents tree:

1. [Description](#description)
2. [Features](#features)
3. [Stack](#stack)
4. [Before you start...](#before-you-start)
5. [Setup guide](#setup)

## Description

This bot is designed to manage Amnezia WireGuard VPN server with advanced obfuscation features to bypass censorship and blocking. It can automatically connect and disconnect users, generate QR codes for mobile clients, and also can be used as a payment system for VPN services.

### Key Features:

- **Amnezia WireGuard Support**: Uses AmneziaWG protocol with built-in obfuscation (Junk Packet Count, Junk Size, Init Sequence Junk, etc.) for better bypassing of VPN blocks
- **Automatic Subscription Management**: Users receive notifications 3 days, 2 days, 1 day before subscription ends, and every 3 hours after expiration
- **Trial Period**: New users get 1 day free trial automatically
- **Referral System**: Invite friends and both get 10 days bonus when they pay for VPN
- **Group Membership Check**: Optional requirement to join Telegram group for using the service
- **Auto-disconnect**: Users are automatically disconnected when subscription expires
- **QR Code Generation**: Mobile-friendly QR codes for easy VPN setup (compatible with AmneziaVPN app)
- **Admin Panel**: Full control over users, subscriptions, and configs

## Stack

Core: python 3.10, aiogram 2.x<br/>
Database: postgresql<br/>
VPN Protocol: Amnezia WireGuard (with obfuscation)<br/>

## Before you start... (if don't want to use semi-automatic installation script)

1. You need to manually install Amnezia WireGuard on your server. The semi-automatic script will install it for you, or you can follow the [AmneziaWG installation guide](https://github.com/amnezia-vpn/amneziawg-tools).
2. You need to configure Amnezia WireGuard server with obfuscation parameters. Configuration guides are available in [Amnezia documentation](https://amnezia.org/).
3. You need to create a bot using [BotFather](https://t.me/BotFather).
4. You need to install [PostgreSQL](https://www.postgresql.org/download/).
5. You need to have poetry installed on your system. You can find installation guide [here](https://python-poetry.org/docs/#installation).
6. Users will need AmneziaVPN client app (available for Android and iOS) to connect to the VPN. Configs are provided as .conf files for easy import.

## Setup

1. You can use semi-automatic installation script or manual installation guide. If you want to use script, just run it and follow the instructions. If you want to install bot manually, follow the instructions below.
   ### Semi-automatic installation script
   
   The script will automatically install Amnezia WireGuard tools and configure everything with obfuscation parameters:
   
   ```bash
   wget https://raw.githubusercontent.com/wireguard-bot/master/SemiAutoInstall.sh && chmod +x SemiAutoInstall.sh && ./SemiAutoInstall.sh
   ```
### Manual installation guide
2. #### Clone this repo and go to project folder<br/>

   ```bash
   git clone https://github.com/wireguard-bot.git && cd wireguard-bot
   ```

3. #### Create your virtualenv inside project dir<br/>

   ```bash
   poetry shell
   ```

4. #### Download required libs<br/>

   ```bash
   poetry install
   ```

5. #### Create your database<br/>

   ```bash
   sudo -u postgres psql
   ```

   ```sql
   CREATE DATABASE <database_name>;
   CREATE USER <user_name> WITH PASSWORD '<password>';
   GRANT ALL PRIVILEGES ON DATABASE <database_name> TO <user_name>;
   GRANT ALL ON ALL TABLES IN SCHEMA "public" TO <user_name>;
   \q
   ```

6. #### Create .env file in data folder and fill it with your data. You can use following example as a template or use .env.sample file (it's the same)<br/>

   ```bash
   cp data/.env.sample data/.env
   nano data/.env
   ```

   #### .env file example

   ```ini
   #telegram bot token
   WG_BOT_TOKEN = <str>
   #ip of your amneziawg server
   WG_SERVER_IP = <str>
   #port of your amneziawg server
   WG_SERVER_PORT = '51830'
   #server's public key (generated with amneziawg)
   WG_SERVER_PUBLIC_KEY = <str>
   #server's preshared key (generated with amneziawg)
   WG_SERVER_PRESHARED_KEY= <str>
   #path to amneziawg config file, default /etc/wireguard/wg0.conf
   WG_CFG_PATH = '/etc/wireguard/wg0.conf'
   #token for telegram invoice payments, if you don't use payments, just leave it empty (NOW IT'S NOT WORKING)
   PAYMENTS_TOKEN = <str>
   #your telegram id, you can get it from @userinfobot or @myidbot or @RawDataBot
   ADMINS_IDS = <str>
   #your bank card number, if you will use payments with "handmade" method
   PAYMENT_CARD = <str>
   #any text you want to show in the start of every peer config file (for example in case MYVPN_user_PC.conf - "MYVPN" is prefix)
   CONFIGS_PREFIX = <str>
   #how much subscription costs in rubles
   BASE_SUBSCRIPTION_MONTHLY_PRICE_RUBLES = <int>
   #dns server for your peers, default 1.1.1.1 if you don't use AdGuard Home, else 10.0.0.1
   PEER_DNS = '1.1.1.1'

   #name of your database
   DATABASE = <str>
   #database user
   DB_USER = <str>
   #database user's password
   DB_USER_PASSWORD = <str>
   #database host, default localhost
   DB_HOST = 'localhost'
   #database port, default 5432
   DB_PORT = '5432'
   
   #optional: telegram group ID that users must join to use the bot
   REQUIRED_GROUP_ID = <int>
   ```

7. #### Configure your database tables<br/>
   Move create script from database/create.py to project root folder and run it

   ```bash
   mv database/create.py . && python3.10 create.py
   ```

   Now you can delete create.py file</br>

   ```bash
   rm create.py
   ```

8. #### Install AdGuard Home (optional)</br>
   Firtly make installation script executable</br>

   ```bash
   chmod +x AdGuardInstall.sh
   ```

   Then run it</br>

   ```bash
   ./AdGuardInstall.sh
   ```
9.  #### Configure AddGuard Home</br>
      Open AddGuard Home web interface on url ```<your_server_ip>:3000```</br>
      Do the initial setup, it's very simple, just follow the instructions and create admin account</br>
      Go to Settings -> Filters -> DNS blocklists and add some blocklists (I recommend to use add all available blocklists EXCEPT `No Google` list)</br>

10. #### Create .service file for your bot</br>
      Path: `/etc/systemd/system/wireguard-bot.service` </br>
      Code: (if you using python 3.10)</br>
   
      ```ini
       [Unit]
       Description='Service for amneziawg bot'
       After=network.target
   
       [Service]
       Type=idle
       Restart=on-failure
       User=root
       ExecStart=/bin/bash -c 'cd ~/wireguard-bot/ && $(poetry env info --path)/bin/python3.10 app.py'
   
       [Install]
       WantedBy=multi-user.target
      ```
11. Enable service and start it</br>
      ```bash
      systemctl enable wireguard-bot.service
      systemctl start wireguard-bot.service
      ```

12. Finally, you can use your bot and enjoy it ❤️

## Extra

### Admin commands (available in chat with bot)

1. `/give <user_id> <days>` - give user access to VPN for <days> days.<br/>
   Also you can use this command with <@username> instead of <user_id>.<br/>
   If you want to disable user's access, just use `/give <user_id> -9999` or any negative number that will be higher than user's access expiration date.<br/>
   <b>WARNING:</b> disconnecting user will not remove his access from database, so you can give him access again later.<br/>
   Example: `/give 123456789 30` - give user with id 123456789 access to VPN for 30 days.
2. `/stats` - show stats about users and their access expiration dates.<br/>
   Aviable options: `/stats active` - show active users.<br/>
   `/stats inactive` - show inactive users.<br/>
   `/stats` without options will show all users.<br/>
   `/wgrestart` - restart amneziawg service

### Referral System

The bot includes a built-in referral program with Amnezia WireGuard support:
- Each user gets a unique referral link: `https://t.me/<bot_username>?start=<user_id>`
- When a referred friend pays for VPN subscription, both users receive 10 bonus days
- Bonuses are automatically added to the subscription end date
- Admins are notified about referral bonuses being awarded
- All generated configs include AmneziaWG obfuscation parameters for bypassing censorship

## Client Applications

Users need to install AmneziaVPN client app on their mobile device:
- **Android**: [Google Play](https://play.google.com/store/apps/details?id=org.amnezia.awg&hl=ru) - Official AmneziaWG client
- **iOS**: [App Store](https://apps.apple.com/ru/app/amneziawg/id6478942365) - Official AmneziaWG client

Configs are provided as `.conf` files that can be directly imported into the app. QR codes are also generated for easy setup on mobile devices.

**Important**: The bot focuses on mobile platforms (Android/iOS) for ease of use. All configs include AmneziaWG obfuscation parameters for bypassing censorship.

## Star History

[![Star History Chart](https://api.star-history.com/svg?repos=wireguard-bot/wireguard-bot&type=Date)](https://star-history.com/#wireguard-bot/wireguard-bot&Date)
