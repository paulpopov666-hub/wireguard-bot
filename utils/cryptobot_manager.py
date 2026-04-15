"""
CryptoBot payment integration module
Supports recurring payments and automatic subscription renewal
"""
from loguru import logger
from data import configuration

# Mock CryptoPay class for compatibility when library is not available
class MockCryptoPay:
    def __init__(self, token):
        self.token = token
    
    async def create_invoice(self, **kwargs):
        logger.warning("CryptoBot mock: invoice creation not available")
        return None
    
    async def get_invoices(self, **kwargs):
        return []


class CryptoBotManager:
    def __init__(self):
        self.token = configuration.cryptobot_token
        if self.token:
            try:
                from cryptopay import CryptoPay
                self.client = CryptoPay(self.token)
            except (ImportError, ModuleNotFoundError):
                logger.warning("CryptoBot library not installed, using mock")
                self.client = MockCryptoPay(self.token)
        else:
            self.client = None
    
    async def create_invoice(self, user_id: int, amount: float, currency: str = "RUB", 
                             description: str = "VPN Subscription", recurring: bool = False):
        """Create payment invoice via CryptoBot"""
        if not self.client:
            return None
        
        try:
            invoice = await self.client.create_invoice(
                amount=amount,
                currency=currency,
                description=description,
                user_id=user_id,
                payload=f"user_{user_id}",
                allow_recurring=recurring
            )
            logger.info(f"Created invoice {invoice.invoice_id} for user {user_id}")
            return invoice
        except Exception as e:
            logger.error(f"Failed to create invoice: {e}")
            return None
    
    async def check_payment_status(self, invoice_id: str):
        """Check if invoice has been paid"""
        if not self.client:
            return False
        
        try:
            invoices = await self.client.get_invoices(invoice_ids=[invoice_id])
            if invoices:
                return invoices[0].status == "paid"
            return False
        except Exception as e:
            logger.error(f"Failed to check payment status: {e}")
            return False
    
    async def get_me(self):
        """Test connection to CryptoBot API"""
        if not self.client:
            return None
        try:
            return await self.client.get_me()
        except Exception as e:
            logger.error(f"CryptoBot connection failed: {e}")
            return None


# Global instance
crypto_bot = CryptoBotManager()
