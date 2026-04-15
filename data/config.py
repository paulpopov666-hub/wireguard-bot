import os
from dotenv import load_dotenv
from loguru import logger


class EnvVariableNotFound(Exception):
    def __init__(self, variable_name: str) -> None:
        super().__init__(f"Environment variable {variable_name} not found in .env file")
        logger.error(f"Environment variable {variable_name} not found in .env file")


class Config:
    def __init__(self) -> None:
        # Load .env file from the data directory
        load_dotenv(os.path.join(os.path.dirname(__file__), '.env'), override=True)

        self._bot_token = self._get_bot_token()
        self._admins = self._get_admins()
        self._payment_card = self._get_payment_card()
        self._configs_prefix = self._get_configs_prefix()
        self._base_subscription_monthly_price_rubles = (
            self._get_base_subscription_monthly_price_rubles()
        )
        self._db_connection_parameters = self._get_db_connection_parameters()
        self._peer_dns = self._get_peer_dns()
        self._required_group_id = self._get_required_group_id()
        self._trial_days = 1  # Trial period in days
        self._payment_method = "manual"  # Only manual payment (screenshots)
        self._obfuscation_params = self._get_obfuscation_params()
        self._amnezia_settings = self._get_amnezia_settings()

    @property
    def bot_token(self) -> str:
        return self._bot_token

    @property
    def admins(self) -> list[int]:
        return self._admins

    @property
    def payment_card(self) -> str:
        return self._payment_card

    @property
    def configs_prefix(self) -> str:
        return self._configs_prefix

    @property
    def base_subscription_monthly_price_rubles(self) -> int:
        return self._base_subscription_monthly_price_rubles

    @property
    def db_connection_parameters(self) -> dict:
        return self._db_connection_parameters

    @property
    def peer_dns(self) -> str:
        return self._peer_dns

    @property
    def required_group_id(self) -> int | None:
        return self._required_group_id

    @property
    def trial_days(self) -> int:
        return self._trial_days

    @property
    def payment_method(self) -> str:
        return "manual"  # Always manual payment

    @property
    def obfuscation_params(self) -> dict:
        return self._obfuscation_params

    @property
    def amnezia_settings(self) -> dict:
        return self._amnezia_settings

    def _get_bot_token(self) -> str:
        bot_token = os.getenv("BOT_TOKEN")
        if not bot_token:
            raise EnvVariableNotFound("BOT_TOKEN")
        return bot_token

    def _get_admins(self) -> list[int]:
        admins_str = os.getenv("ADMINS")
        if not admins_str:
            raise EnvVariableNotFound("ADMINS")
        return list(map(int, [admin for admin in admins_str.split(",") if admin]))

    def _get_payment_card(self) -> str:
        payment_card = os.getenv("PAYMENT_CARD", "")
        return payment_card

    def _get_configs_prefix(self) -> str:
        configs_prefix = os.getenv("CONFIGS_PREFIX", "wg_config")
        return configs_prefix

    def _get_db_connection_parameters(self) -> dict:
        db_connection_parameters = {
            "host": os.getenv("DB_HOST", "localhost"),
            "port": os.getenv("DB_PORT", "5432"),
            "user": os.getenv("DB_USER", "postgres"),
            "password": os.getenv("DB_USER_PASSWORD", ""),
            "database": os.getenv("DATABASE", "vpnbot"),
        }
        return db_connection_parameters

    def _get_base_subscription_monthly_price_rubles(self) -> int:
        base_subscription_monthly_price_rubles = os.getenv(
            "BASE_SUBSCRIPTION_MONTHLY_PRICE_RUBLES", "299"
        )
        return int(base_subscription_monthly_price_rubles)

    def _get_peer_dns(self) -> str:
        peer_dns = os.getenv("PEER_DNS", "8.8.8.8")
        return peer_dns

    def _get_required_group_id(self) -> int | None:
        """Get required Telegram group ID for subscription"""
        group_id = os.getenv("REQUIRED_GROUP_ID")
        if not group_id:
            logger.warning("REQUIRED_GROUP_ID not found in .env file, group membership check disabled")
            return None
        try:
            return int(group_id)
        except ValueError:
            logger.error(f"Invalid REQUIRED_GROUP_ID value: {group_id}")
            return None

    def _get_obfuscation_params(self) -> dict:
        """Get AmneziaWG obfuscation parameters (AmneziaWG 2.0 format)"""
        params = {
            "h1": os.getenv("OBFUSCATION_H1", "646561924-646573803"),
            "h2": os.getenv("OBFUSCATION_H2", "1946678917-1946711958"),
            "h3": os.getenv("OBFUSCATION_H3", "2485102049-2485121055"),
            "h4": os.getenv("OBFUSCATION_H4", "3974564915-3974609527"),
            "s1": int(os.getenv("OBFUSCATION_S1", "14")),
            "s2": int(os.getenv("OBFUSCATION_S2", "117")),
            "s3": int(os.getenv("OBFUSCATION_S3", "64")),
            "s4": int(os.getenv("OBFUSCATION_S4", "11")),
            "jc": int(os.getenv("OBFUSCATION_JC", "5")),
            "jmin": int(os.getenv("OBFUSCATION_JMIN", "320")),
            "jmax": int(os.getenv("OBFUSCATION_JMAX", "795")),
            "i1": os.getenv("OBFUSCATION_I1", "<b 0xc3000000011367b46e67578c05c2fcb734cf9bed45ff4c8cce0288f60082699e76><rc 14><t><r 1000><r 201>"),
            "i2": os.getenv("OBFUSCATION_I2", "<b 0xc20000000108fc7b0c89c6d2ee58096efa819b42b372c2de11be120f5c964f4950418e00c805ca82431faca9ea68><rc 14><t><r 1000><r 186>"),
            "i3": os.getenv("OBFUSCATION_I3", "<b 0xc3000000010c885286dd36f1b50b27518dd50d493fb82f818aa6c5d96db7da130058089bb3><rc 19><t><r 1000><r 191>"),
            "i4": os.getenv("OBFUSCATION_I4", "<b 0xc2000000010cd62091ab627f57efb52082fd04050efc050023b74572><rc 18><t><r 1000><r 201>"),
            "i5": os.getenv("OBFUSCATION_I5", "<b 0xc0000000010bc01af1c16c14a0a6262c2801f316af2ab4f371efc0af7faac73f4799d01bbf89ec4ff3fd92d46e45><rc 13><t><r 1000><r 189>"),
        }
        return params

    def _get_amnezia_settings(self) -> dict:
        """Get Amnezia WireGuard server settings for SSH connection"""
        settings = {
            "host": os.getenv("AMNEZIA_HOST", "127.0.0.1"),
            "port": int(os.getenv("AMNEZIA_PORT", "22")),
            "user": os.getenv("AMNEZIA_USER", "root"),
            "password": os.getenv("AMNEZIA_PASSWORD", ""),
            "service_name": os.getenv("AMNEZIA_SERVICE_NAME", "wireguard"),
        }
        return settings
