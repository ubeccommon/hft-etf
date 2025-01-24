import os
from pathlib import Path
from dotenv import load_dotenv
from models.etf_assetlist import DynamicAssetManager, ETF_ASSETLIST

# Get the absolute path to the .env file
env_path = Path(__file__).parent.parent / '.env'

# Load environment variables from .env file
if not load_dotenv(env_path):
    raise RuntimeError(f"Could not load .env file at {env_path}")

class Config:
    # Asset Configuration
    ETF_ASSETLIST = ETF_ASSETLIST

    # Load Stellar Network Configuration
    NETWORK_PASSPHRASE = os.getenv('STELLAR_NETWORK_PASSPHRASE')
    if not NETWORK_PASSPHRASE:
        NETWORK_PASSPHRASE = 'Public Global Stellar Network ; September 2015'

    HORIZON_SERVER = os.getenv('STELLAR_HORIZON_SERVER')
    if not HORIZON_SERVER:
        HORIZON_SERVER = 'https://horizon.stellar.org'
    
    # Load Security Configuration
    SECRET_KEY = os.getenv('STELLAR_SECRET_KEY')
    if not SECRET_KEY:
        raise ValueError("STELLAR_SECRET_KEY must be set in .env file")

    # Load Trading Configuration with defaults
    try:
        ARBITRAGE_THRESHOLD = float(os.getenv('ARBITRAGE_THRESHOLD', '0.005'))
        ALLOCATION_TOLERANCE = float(os.getenv('ALLOCATION_TOLERANCE', '0.02'))
        MAX_TRANSACTION_FEE = int(os.getenv('MAX_TRANSACTION_FEE', '100'))
    except ValueError as e:
        raise ValueError(f"Invalid trading configuration in .env file: {str(e)}")
    
    # Load Logging Configuration
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')

    @classmethod
    def verify_env_variables(cls):
        """Verify all environment variables are loaded correctly"""
        required_vars = {
            'STELLAR_NETWORK_PASSPHRASE': cls.NETWORK_PASSPHRASE,
            'STELLAR_HORIZON_SERVER': cls.HORIZON_SERVER,
            'STELLAR_SECRET_KEY': cls.SECRET_KEY,
            'ARBITRAGE_THRESHOLD': cls.ARBITRAGE_THRESHOLD,
            'ALLOCATION_TOLERANCE': cls.ALLOCATION_TOLERANCE,
            'MAX_TRANSACTION_FEE': cls.MAX_TRANSACTION_FEE,
            'LOG_LEVEL': cls.LOG_LEVEL
        }
        
        for var_name, value in required_vars.items():
            if value is None:
                raise ValueError(f"Required environment variable {var_name} is not set in .env file")
        
        # Print loaded configuration
        print("\nLoaded Configuration:")
        print(f"Network: {cls.NETWORK_PASSPHRASE}")
        print(f"Horizon: {cls.HORIZON_SERVER}")
        print(f"Arbitrage Threshold: {cls.ARBITRAGE_THRESHOLD}")
        print(f"Allocation Tolerance: {cls.ALLOCATION_TOLERANCE}")
        print(f"Max Transaction Fee: {cls.MAX_TRANSACTION_FEE}")
        print(f"Log Level: {cls.LOG_LEVEL}")
        print("Secret Key: [SECURED]\n")

    @classmethod
    def get_asset_allocations(cls):
        """Dynamically retrieve enabled asset allocations"""
        enabled_assets = dynamic_asset_manager.get_enabled_assets()
        return {
            asset['asset_code']: asset['allocation'] 
            for asset in enabled_assets
        }

    @classmethod
    def validate_configuration(cls):
        """Validate the entire configuration"""
        try:
            # Verify environment variables
            cls.verify_env_variables()
            
            # Validate configuration values
            if cls.ARBITRAGE_THRESHOLD <= 0:
                raise ValueError("ARBITRAGE_THRESHOLD must be greater than 0")
            if cls.ALLOCATION_TOLERANCE <= 0:
                raise ValueError("ALLOCATION_TOLERANCE must be greater than 0")
            if cls.MAX_TRANSACTION_FEE <= 0:
                raise ValueError("MAX_TRANSACTION_FEE must be greater than 0")
            
            # Validate ETF asset list
            if not cls.ETF_ASSETLIST:
                raise ValueError("ETF_ASSETLIST is not properly initialized")
            
            # Validate total allocation
            enabled_allocation = sum(
                asset['allocation'] for asset in cls.ETF_ASSETLIST 
                if asset['enabled']
            )
            if abs(enabled_allocation - 1.0) > 0.0001:
                raise ValueError(f"Total allocation must equal 1.0, got {enabled_allocation}")
            
            return True
        except Exception as e:
            raise ValueError(f"Configuration validation failed: {str(e)}")

# Initialize dynamic asset manager
dynamic_asset_manager = DynamicAssetManager()

# Create configuration instance and validate
config = Config()
config.validate_configuration()

# Export configuration
__all__ = ['Config', 'config']
