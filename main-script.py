import time
from config.config import Config
from core.etf_manager import ETFManager
from services.logging_service import logging_service

def run_etf_bot():
    """Main entry point for Stellar ETF Bot"""
    try:
        etf_bot = ETFManager(
            network_passphrase=Config.NETWORK_PASSPHRASE,
            server_endpoint=Config.HORIZON_SERVER
        )
        
        while True:
            try:
                # Execute ETF strategy
                etf_bot.execute_etf_strategy()
                
                # Wait before next iteration
                time.sleep(Config.ARBITRAGE_THRESHOLD * 3600)  # Convert threshold to hours
            
            except Exception as e:
                logging_service.error(f"ETF Bot Execution Error: {str(e)}")
                time.sleep(60)  # Wait 1 minute before retry
                
    except Exception as e:
        logging_service.error(f"Critical Error: {str(e)}")
        raise

if __name__ == '__main__':
    logging_service.info("Stellar ETF Bot Starting...")
    run_etf_bot()
