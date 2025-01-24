from decimal import Decimal
from services.stellar_service import stellar_service
from services.market_data_service import market_data_service
from core.arbitrage_engine import ArbitrageEngine
from core.transaction_executor import TransactionExecutor
from utils.error_handler import handle_transaction_error
from services.logging_service import logging_service
from config.config import Config

class ETFManager:
    def __init__(self, network_passphrase, server_endpoint):
        self.stellar_network = stellar_service
        self.arbitrage_engine = ArbitrageEngine(self.stellar_network)
        self.transaction_executor = TransactionExecutor(self.stellar_network)
        self.target_allocations = Config.get_asset_allocations()

    def _analyze_allocation_drift(self, current_portfolio):
        """Detect portfolio allocation deviations"""
        discrepancies = {}
        for asset, target_percentage in self.target_allocations.items():
            try:
                current = Decimal(str(current_portfolio.get(asset, '0')))
                target = Decimal(str(target_percentage))
                
                if abs(current - target) > Decimal(str(Config.ALLOCATION_TOLERANCE)):
                    discrepancies[asset] = {
                        'current': str(current),
                        'target': str(target),
                        'difference': str(abs(current - target)),
                        'direction': 'increase' if current < target else 'decrease'
                    }
                    logging_service.info(
                        f"Drift detected for {asset}: "
                        f"current={current:.7f}, target={target:.7f}, "
                        f"difference={abs(current - target):.7f}"
                    )
            except Exception as e:
                logging_service.error(f"Error analyzing drift for {asset}: {str(e)}")
                continue
                
        return discrepancies

    def _calculate_rebalance_pairs(self, current_portfolio):
        """Calculate which assets need rebalancing and pair them for path payments"""
        over_allocated = []
        under_allocated = []
        
        for asset, target in self.target_allocations.items():
            current = Decimal(str(current_portfolio.get(asset, '0')))
            target = Decimal(str(target))
            difference = current - target
            
            if abs(difference) > Decimal(str(Config.ALLOCATION_TOLERANCE)):
                if difference > 0:
                    over_allocated.append((asset, difference))
                    logging_service.info(f"Over-allocated: {asset} by {difference:.7f}")
                else:
                    under_allocated.append((asset, abs(difference)))
                    logging_service.info(f"Under-allocated: {asset} by {abs(difference):.7f}")
        
        # Sort by size of deviation to handle largest imbalances first
        over_allocated.sort(key=lambda x: x[1], reverse=True)
        under_allocated.sort(key=lambda x: x[1], reverse=True)
        
        rebalance_pairs = []
        while over_allocated and under_allocated:
            source_asset, source_excess = over_allocated[0]
            dest_asset, dest_deficit = under_allocated[0]
            
            # Determine amount to transfer (as a percentage)
            amount = min(source_excess, dest_deficit)
            
            if amount >= Decimal('0.0000001'):  # Stellar's minimum amount
                rebalance_pairs.append({
                    'source_asset': source_asset,
                    'destination_asset': dest_asset,
                    'amount': str(amount),
                    'source_pct': str(source_excess),
                    'dest_pct': str(dest_deficit)
                })
                
                logging_service.info(
                    f"Created rebalance pair: {source_asset} -> {dest_asset}, "
                    f"amount: {amount:.7f}"
                )
            
            # Update remaining imbalances
            if source_excess > dest_deficit:
                over_allocated[0] = (source_asset, source_excess - dest_deficit)
                under_allocated.pop(0)
            else:
                under_allocated[0] = (dest_asset, dest_deficit - source_excess)
                over_allocated.pop(0)
                
        return rebalance_pairs

    def _rebalance_portfolio(self, discrepancies):
        """Execute portfolio rebalancing using path payments"""
        try:
            current_portfolio = self.stellar_network.get_portfolio_composition()
            rebalance_pairs = self._calculate_rebalance_pairs(current_portfolio)
            
            for pair in rebalance_pairs:
                try:
                    logging_service.info(
                        f"Attempting rebalance: {pair['amount']} from "
                        f"{pair['source_asset']} ({pair['source_pct']}%) to "
                        f"{pair['destination_asset']} ({pair['dest_pct']}%)"
                    )
                    
                    # Create path payment
                    path_payment = {
                        'source_asset': pair['source_asset'],
                        'destination_asset': pair['destination_asset'],
                        'send_amount': pair['amount'],
                        'destination': self.stellar_network.public_key
                    }
                    
                    # Execute the path payment
                    result = self.transaction_executor.execute_path_payment(path_payment)
                    if result:
                        logging_service.info(
                            f"Successfully rebalanced {pair['amount']} from "
                            f"{pair['source_asset']} to {pair['destination_asset']}"
                        )
                    
                except Exception as e:
                    logging_service.error(
                        f"Failed to execute rebalance between "
                        f"{pair['source_asset']} and {pair['destination_asset']}: {str(e)}"
                    )
                    
        except Exception as e:
            handle_transaction_error(e, "Portfolio Rebalancing")

    def execute_etf_strategy(self):
        """Core high-frequency ETF strategy execution"""
        try:
            # Current portfolio assessment
            current_portfolio = self.stellar_network.get_portfolio_composition()
            logging_service.info(f"Current portfolio composition: {current_portfolio}")
            logging_service.info(f"Target allocations: {self.target_allocations}")
            
            # Detect deviation from target allocation
            allocation_discrepancies = self._analyze_allocation_drift(current_portfolio)
            
            if allocation_discrepancies:
                logging_service.info(f"Detected allocation discrepancies: {allocation_discrepancies}")
                self._rebalance_portfolio(allocation_discrepancies)
            else:
                logging_service.info("Portfolio is within target allocations")
            
            # Identify arbitrage opportunities
            arbitrage_paths = self.arbitrage_engine.find_profitable_paths(
                current_portfolio, 
                threshold=Config.ARBITRAGE_THRESHOLD
            )
            
            # Execute transactions
            for path in arbitrage_paths:
                self.transaction_executor.execute_path_payment(path)
            
        except Exception as e:
            handle_transaction_error(e, "ETF Strategy Execution")

# Export the ETFManager class
__all__ = ['ETFManager']
