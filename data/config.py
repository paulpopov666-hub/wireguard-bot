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
        self._cryptobot_token = self._get_cryptobot_token()
        self._payment_method = self._get_payment_method()  # 'manual' or 'cryptobot'
        self._obfuscation_params = self._get_obfuscation_params()

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
    def cryptobot_token(self) -> str | None:
        return self._cryptobot_token

    @property
    def payment_method(self) -> str:
        return self._payment_method

    @property
    def obfuscation_params(self) -> dict:
        return self._obfuscation_params

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
        # Return empty string if not set (optional for cryptobot mode)
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

    def _get_cryptobot_token(self) -> str | None:
        """Get CryptoBot API token"""
        token = os.getenv("CRYPTOBOT_TOKEN")
        if not token:
            logger.warning("CRYPTOBOT_TOKEN not found in .env file, CryptoBot payments disabled")
            return None
        return token

    def _get_payment_method(self) -> str:
        """Get payment method: 'manual' (screenshots) or 'cryptobot'"""
        method = os.getenv("PAYMENT_METHOD", "manual").lower()
        if method not in ["manual", "cryptobot"]:
            logger.warning(f"Invalid PAYMENT_METHOD '{method}', defaulting to 'manual'")
            return "manual"
        return method

    def _get_obfuscation_params(self) -> dict:
        """Get AmneziaWG obfuscation parameters"""
        params = {
            "jc": int(os.getenv("OBFUSCATION_JC", "10")),
            "jmin": int(os.getenv("OBFUSCATION_JMIN", "5")),
            "jmax": int(os.getenv("OBFUSCATION_JMAX", "20")),
            "s1": int(os.getenv("OBFUSCATION_S1", "30")),
            "s2": int(os.getenv("OBFUSCATION_S2", "40")),
            "h1": int(os.getenv("OBFUSCATION_H1", "1")),
            "h2": int(os.getenv("OBFUSCATION_H2", "2")),
            "h3": int(os.getenv("OBFUSCATION_H3", "3")),
            "h4": int(os.getenv("OBFUSCATION_H4", "4")),
        }
        return params
