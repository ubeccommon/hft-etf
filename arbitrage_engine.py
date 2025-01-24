from services.market_data_service import market_data_service
from services.logging_service import logging_service
from config.config import Config

class ArbitrageEngine:
    def __init__(self, stellar_service):
        self.stellar_service = stellar_service
    
    def find_profitable_paths(self, current_portfolio, threshold=Config.ARBITRAGE_THRESHOLD):
        """
        Detect arbitrage opportunities across different trading paths
        
        Args:
            current_portfolio (dict): Current asset allocation
            threshold (float): Minimum profit percentage to execute
        
        Returns:
            list: Profitable arbitrage paths
        """
        try:
            # Retrieve market prices for assets
            market_prices = market_data_service.get_current_prices()
            
            profitable_paths = []
            
            # Cross-asset arbitrage detection
            for source_asset in current_portfolio:
                for target_asset in market_prices:
                    if source_asset != target_asset:
                        profit_percentage = self._calculate_arbitrage_opportunity(
                            source_asset, 
                            target_asset, 
                            market_prices
                        )
                        
                        if profit_percentage > threshold:
                            path = {
                                'source_asset': source_asset,
                                'target_asset': target_asset,
                                'profit_percentage': profit_percentage
                            }
                            profitable_paths.append(path)
                            logging_service.info(f"Found profitable arbitrage path: {path}")
            
            return profitable_paths
        
        except Exception as e:
            logging_service.error(f"Error in arbitrage path detection: {e}")
            return []
    
    def _calculate_arbitrage_opportunity(self, source_asset, target_asset, market_prices):
        """Calculate potential arbitrage profit"""
        try:
            source_price = market_prices[source_asset]
            target_price = market_prices[target_asset]
            
            # Simple cross-asset price comparison
            conversion_rate = source_price / target_price
            profit_percentage = (conversion_rate - 1) * 100
            
            return profit_percentage
        except Exception as e:
            logging_service.error(f"Error calculating arbitrage opportunity: {e}")
            return 0.0
