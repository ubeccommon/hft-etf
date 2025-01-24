from services.logging_service import logging_service
from config import config

def validate_transaction(transaction_details):
    """
    Validate transaction parameters
    
    Args:
        transaction_details (dict): Transaction details to validate
    
    Raises:
        ValueError: If transaction fails validation
    """
    try:
        # Check for required keys
        required_keys = ['source_asset', 'target_asset', 'profit_percentage']
        for key in required_keys:
            if key not in transaction_details:
                raise ValueError(f"Missing required key: {key}")
        
        # Validate profit percentage
        profit_percentage = transaction_details['profit_percentage']
        if profit_percentage < config.ARBITRAGE_THRESHOLD:
            raise ValueError(f"Profit percentage {profit_percentage}% below threshold")
        
        # Additional validation logic can be added here
    except Exception as e:
        logging_service.log_error(
            e, 
            context=f"Transaction Validation: {transaction_details}"
        )
        raise
