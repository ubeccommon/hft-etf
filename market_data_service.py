import requests
from services.logging_service import logging_service

class MarketDataService:
    def __init__(self):
        self.price_sources = [
            'https://api.coingecko.com/api/v3/simple/price',
            'https://api.binance.com/api/v3/ticker/price'
        ]
    
    def get_current_prices(self, assets=None):
        """
        Retrieve current market prices for specified assets
        
        Args:
            assets (list): List of asset codes to retrieve prices for
        
        Returns:
            dict: Current market prices
        """
        if assets is None:
            assets = ['XLM', 'USDC', 'BTC', 'ETH']
        
        prices = {}
        for source in self.price_sources:
            try:
                response = requests.get(source, params={'ids': assets})
                if response.status_code == 200:
                    prices.update(response.json())
                    break
            except Exception as e:
                logging_service.log_error(
                    e, 
                    context=f"Price Retrieval from {source}"
                )
        
        return prices

market_data_service = MarketDataService()
