from services.logging_service import logging_service

def handle_transaction_error(error, info=None):
    """
    Centralized error handling for Stellar transactions
    
    Args:
        error: The exception that was raised
        info: Optional additional information about the error
    """
    error_info = {
        'error_type': type(error).__name__,
        'error_message': str(error),
        'additional_info': info
    }
    
    logging_service.error(f"Transaction Error: {error_info}")
    
    if hasattr(error, 'response') and error.response:
        try:
            response_data = error.response.json()
            logging_service.error("Stellar API Error Details", str(response_data))
        except:
            pass

    # Re-raise the error for upstream handling
    raise error
