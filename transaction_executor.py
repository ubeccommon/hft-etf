from decimal import Decimal
from services.logging_service import logging_service
from stellar_sdk import (
    Asset, Server, TransactionBuilder, Operation, PathPaymentStrictSend
)

class TransactionExecutor:
    def __init__(self, stellar_service):
        self.stellar_service = stellar_service

    def get_path_payment_min_amount(self, source_asset_code, destination_asset_code, send_amount):
        """Calculate minimum destination amount based on strict send path"""
        try:
            # Create assets
            source_asset = self.stellar_service.create_asset(source_asset_code)
            destination_asset = self.stellar_service.create_asset(destination_asset_code)
            formatted_amount = self.stellar_service.format_stellar_amount(send_amount)

            # Get paths using correct parameters
            paths_response = self.stellar_service.server.strict_send_paths(
                source_asset=source_asset,
                source_amount=formatted_amount,
                destination=[destination_asset]  # Changed from destination_assets to destination
            ).call()
            
            if not paths_response.get('_embedded', {}).get('records', []):
                logging_service.error(f"No path found from {source_asset_code} to {destination_asset_code}")
                return None, []

            # Get the best path's destination amount
            best_path = paths_response['_embedded']['records'][0]
            dest_amount = best_path['destination_amount']

            # Apply 1% slippage tolerance
            min_amount = Decimal(dest_amount) * Decimal('0.99')
            formatted_min = self.stellar_service.format_stellar_amount(min_amount)

            logging_service.info(
                f"Path found: {formatted_amount} {source_asset_code} -> "
                f"{formatted_min} {destination_asset_code} (path: {best_path.get('path', [])})"
            )

            return formatted_min, best_path.get('path', [])

        except Exception as e:
            logging_service.error(f"Error calculating minimum amount: {str(e)}")
            return None, []

    def execute_path_payment(self, payment_details):
        """Execute a path payment for rebalancing"""
        try:
            if not self._validate_path_payment(payment_details):
                logging_service.error("Invalid path payment details")
                return None

            # Format send amount
            send_amount = self.stellar_service.format_stellar_amount(payment_details['send_amount'])
            
            # Skip if amount is too small
            if Decimal(send_amount) < Decimal('0.0000001'):
                logging_service.warning(f"Amount {send_amount} too small for {payment_details['source_asset']}, skipping")
                return None

            # Calculate minimum destination amount and path
            dest_min, path = self.get_path_payment_min_amount(
                payment_details['source_asset'],
                payment_details['destination_asset'],
                send_amount
            )

            if not dest_min:
                logging_service.error("Could not determine minimum destination amount")
                return None

            # Create assets
            source_asset = self.stellar_service.create_asset(payment_details['source_asset'])
            destination_asset = self.stellar_service.create_asset(payment_details['destination_asset'])

            # Load account
            account = self.stellar_service.server.load_account(self.stellar_service.public_key)

            # Build path payment operation
            path_payment_op = PathPaymentStrictSend(
                destination=payment_details['destination'],
                send_asset=source_asset,
                send_amount=send_amount,
                dest_asset=destination_asset,
                dest_min=dest_min,
                path=path
            )

            # Create transaction
            transaction = (
                TransactionBuilder(
                    source_account=account,
                    network_passphrase=self.stellar_service.network_passphrase,
                    base_fee=self.stellar_service.MAX_TRANSACTION_FEE
                )
                .append_operation(path_payment_op)
                .set_timeout(30)
                .build()
            )

            # Sign and submit transaction
            transaction.sign(self.stellar_service.keypair)
            
            logging_service.info(
                f"Submitting path payment: {send_amount} {payment_details['source_asset']} -> "
                f"min {dest_min} {payment_details['destination_asset']}"
            )
            
            response = self.stellar_service.submit_transaction(transaction)

            logging_service.info(
                f"Path payment executed: {send_amount} "
                f"{payment_details['source_asset']} -> {payment_details['destination_asset']} "
                f"(hash: {response.get('hash', 'unknown')})"
            )

            return response

        except Exception as e:
            logging_service.error(f"Failed to execute path payment: {str(e)}")
            raise

    # Rest of the class remains the same...
    def _validate_path_payment(self, payment_details):
        """Validate path payment details"""
        try:
            required_fields = [
                'source_asset', 'destination_asset', 
                'send_amount', 'destination'
            ]
            if not all(field in payment_details for field in required_fields):
                logging_service.error(f"Missing required fields: {required_fields}")
                return False
                
            # Validate amount can be converted to Decimal
            Decimal(str(payment_details['send_amount']))
            return True
            
        except Exception as e:
            logging_service.error(f"Payment validation error: {str(e)}")
            return False

    def execute_transaction(self, transaction):
        """Execute a regular transaction"""
        if not transaction:
            logging_service.info("Skipping empty transaction")
            return None
            
        try:
            response = self.stellar_service.submit_transaction(transaction)
            logging_service.info(f"Transaction executed: {response.get('hash', 'No hash')}")
            return response
        except Exception as e:
            logging_service.error(f"Transaction execution failed: {str(e)}")
            raise

