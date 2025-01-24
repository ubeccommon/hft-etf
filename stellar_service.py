from decimal import Decimal, ROUND_DOWN
from stellar_sdk import Server, Keypair, TransactionBuilder, Asset, PathPaymentStrictSend
from services.logging_service import logging_service
from config.config import Config

class StellarService:
    def __init__(self, network_passphrase=Config.NETWORK_PASSPHRASE, 
                 server_endpoint=Config.HORIZON_SERVER):
        self.network_passphrase = network_passphrase
        self.server = Server(horizon_url=server_endpoint)
        self.MAX_TRANSACTION_FEE = Config.MAX_TRANSACTION_FEE
        
        if not Config.SECRET_KEY:
            error_msg = "Stellar secret key not found in environment variables"
            logging_service.error(error_msg)
            raise ValueError(error_msg)
            
        try:
            self.keypair = Keypair.from_secret(Config.SECRET_KEY)
            self.public_key = self.keypair.public_key
            logging_service.info("Stellar account initialized successfully")
        except Exception as e:
            logging_service.error(f"Error initializing Stellar account: {str(e)}")
            raise

    def get_account_details(self):
        """Retrieve account details from Stellar network"""
        try:
            response = self.server.accounts().account_id(self.public_key).call()
            return {
                'sequence': response['sequence'],
                'balances': response['balances']
            }
        except Exception as e:
            logging_service.error(f"Failed to retrieve account details: {str(e)}")
            raise

    def get_portfolio_composition(self):
        """
        Analyze current portfolio asset allocation
        Returns dict with asset codes as keys and allocation percentages as values
        """
        try:
            account_details = self.get_account_details()
            portfolio = {}
            
            # Convert balances to Decimal for precise arithmetic
            total_balance = Decimal('0')
            for balance in account_details['balances']:
                balance_amount = Decimal(str(balance.get('balance', '0')))
                total_balance += balance_amount
            
            for balance in account_details['balances']:
                asset_code = balance.get('asset_type', 'native')
                if asset_code == 'native':
                    asset_code = 'XLM'
                else:
                    asset_code = balance.get('asset_code', 'XLM')
                    
                balance_amount = Decimal(str(balance.get('balance', '0')))
                if total_balance > 0:
                    portfolio[asset_code] = float(balance_amount / total_balance)
            
            logging_service.info(f"Portfolio composition retrieved: {portfolio}")
            return portfolio
        except Exception as e:
            logging_service.error(f"Failed to compute portfolio composition: {str(e)}")
            raise

    def get_asset_issuer(self, asset_code):
        """Get issuer for a specific asset code"""
        try:
            asset_info = next(
                (asset for asset in Config.ETF_ASSETLIST 
                 if asset['asset_code'] == asset_code),
                None
            )
            if not asset_info:
                logging_service.error(f"Asset {asset_code} not found in ETF asset list")
                return None
            return asset_info['issuer']
        except Exception as e:
            logging_service.error(f"Error getting issuer for {asset_code}: {str(e)}")
            return None

    def format_stellar_amount(self, amount):
        """Format amount to Stellar's 7 decimal place precision"""
        try:
            decimal_amount = Decimal(str(amount))
            formatted_amount = decimal_amount.quantize(Decimal('0.0000001'), rounding=ROUND_DOWN)
            return str(formatted_amount)
        except Exception as e:
            logging_service.error(f"Error formatting amount: {str(e)}")
            raise ValueError(f"Invalid amount format: {amount}")

    def create_asset(self, asset_code):
        """Create Stellar SDK Asset object"""
        try:
            if asset_code.upper() == 'XLM':
                return Asset.native()
            
            issuer = self.get_asset_issuer(asset_code)
            if not issuer:
                raise ValueError(f"No issuer found for asset {asset_code}")
                
            return Asset(asset_code, issuer)
        except Exception as e:
            logging_service.error(f"Failed to create asset {asset_code}: {str(e)}")
            raise

    def create_path_payment(self, source_asset_code, destination_asset_code, send_amount, destination):
        """Create a path payment transaction"""
        try:
            # Format amount
            formatted_amount = self.format_stellar_amount(send_amount)
            
            # Create assets
            source_asset = self.create_asset(source_asset_code)
            destination_asset = self.create_asset(destination_asset_code)
            
            # Skip if amount is too small
            if Decimal(formatted_amount) < Decimal('0.0000001'):
                logging_service.warning(f"Amount {formatted_amount} too small for path payment, skipping")
                return None
            
            # Load account
            account = self.server.load_account(self.public_key)
            
            # Create path payment operation
            path_payment_op = PathPaymentStrictSend(
                destination=destination,
                send_asset=source_asset,
                send_amount=formatted_amount,
                dest_asset=destination_asset,
                dest_min=formatted_amount,  # Set minimum to same as send amount
                path=[]  # Empty path for direct payment
            )
            
            # Build transaction
            transaction = (
                TransactionBuilder(
                    source_account=account,
                    network_passphrase=self.network_passphrase,
                    base_fee=self.MAX_TRANSACTION_FEE
                )
                .append_operation(path_payment_op)
                .set_timeout(30)
                .build()
            )
            
            # Sign transaction
            transaction.sign(self.keypair)
            return transaction
            
        except Exception as e:
            logging_service.error(f"Failed to create path payment: {str(e)}")
            raise

    def submit_transaction(self, transaction):
        """Submit signed transaction to Stellar network"""
        try:
            if transaction is None:
                return None
                
            response = self.server.submit_transaction(transaction)
            logging_service.info(f"Transaction {response['hash']} submitted successfully")
            return response
        except Exception as e:
            logging_service.error(f"Failed to submit transaction: {str(e)}")
            raise

# Create singleton instance
stellar_service = StellarService()

# Export the class and instance
__all__ = ['StellarService', 'stellar_service']
