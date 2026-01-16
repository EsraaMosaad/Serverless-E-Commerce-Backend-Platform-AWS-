"""
Process Payment Handler - Step Functions Task
Developer 1: Backend Core & Orchestration

This Lambda function processes payment for validated orders.
Currently implements a MOCK payment gateway for testing.

In production, you would integrate with:
- Stripe
- PayPal
- Square
- or other payment processors

This function is called by Step Functions after order validation.
"""

import json
import os
import time
import hashlib
from datetime import datetime
from decimal import Decimal
from typing import Dict, Any
import random

# Custom JSON encoder to handle Decimal types
class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        return super(DecimalEncoder, self).default(obj)


def lambda_handler(event, context):
    """
    Main Lambda handler function
    
    Input (from Step Functions):
    {
        "orderId": "order-123",
        "userId": "user-456",
        "items": [...],
        "totalAmount": 59.98,
        "validationResult": {...}
    }
    
    Output (to Step Functions):
    {
        "orderId": "order-123",
        "userId": "user-456",
        "items": [...],
        "totalAmount": 59.98,
        "validationResult": {...},
        "paymentResult": {
            "status": "success" | "failed",
            "transactionId": "txn-xxx",
            "processedAt": "2024-01-16T10:00:00Z",
            "provider": "mock-payment-gateway",
            "message": "Payment processed successfully"
        }
    }
    """
    
    print(f"Processing payment for order: {json.dumps(event, cls=DecimalEncoder)}")
    
    try:
        order_id = event.get('orderId')
        user_id = event.get('userId')
        total_amount = event.get('totalAmount', 0)
        
        # Simulate payment processing
        payment_result = process_payment(
            order_id=order_id,
            user_id=user_id,
            amount=total_amount
        )
        
        # Build response with payment result
        response = {
            **event,  # Include all original fields
            'paymentResult': payment_result
        }
        
        # Log result
        if payment_result['status'] == 'success':
            print(f"✅ Payment successful for order {order_id}: {payment_result['transactionId']}")
        else:
            print(f"❌ Payment failed for order {order_id}: {payment_result['message']}")
            # Raise exception so Step Functions can catch it
            raise ValueError(f"Payment failed: {payment_result['message']}")
        
        return response
        
    except Exception as e:
        print(f"Error processing payment: {str(e)}")
        raise


def process_payment(order_id: str, user_id: str, amount: float) -> Dict[str, Any]:
    """
    Mock payment processing function
    
    In production, this would:
    1. Call external payment gateway API (Stripe, PayPal, etc.)
    2. Handle authentication and encryption
    3. Process card/payment method
    4. Return real transaction ID
    
    For testing, this mock:
    - Simulates 90% success rate
    - Generates fake transaction IDs
    - Adds realistic delays
    """
    
    # Simulate processing delay (payment gateway response time)
    time.sleep(0.2)  # 200ms delay
    
    # Generate a unique transaction ID
    transaction_id = generate_transaction_id(order_id, user_id)
    
    # Simulate payment success/failure
    # 90% success rate for realistic testing
    is_successful = random.random() < 0.90
    
    if is_successful:
        return {
            'status': 'success',
            'transactionId': transaction_id,
            'processedAt': datetime.utcnow().isoformat() + 'Z',
            'provider': 'mock-payment-gateway',
            'message': f'Payment of ${amount:.2f} processed successfully',
            'amount': amount,
            'currency': 'USD'
        }
    else:
        # Simulate various failure reasons
        failure_reasons = [
            'Insufficient funds',
            'Card declined',
            'Payment gateway timeout',
            'Invalid card details',
            'Bank authorization failed'
        ]
        
        failure_reason = random.choice(failure_reasons)
        
        return {
            'status': 'failed',
            'transactionId': transaction_id,
            'processedAt': datetime.utcnow().isoformat() + 'Z',
            'provider': 'mock-payment-gateway',
            'message': f'Payment failed: {failure_reason}',
            'failureReason': failure_reason,
            'amount': amount,
            'currency': 'USD'
        }


def generate_transaction_id(order_id: str, user_id: str) -> str:
    """
    Generate a unique transaction ID
    
    In production, this would come from the payment gateway.
    For testing, we generate a deterministic but unique ID.
    """
    # Create a hash from order_id, user_id, and timestamp
    timestamp = str(int(time.time() * 1000))  # milliseconds
    data = f"{order_id}-{user_id}-{timestamp}"
    
    # Generate hash
    hash_object = hashlib.sha256(data.encode())
    hash_hex = hash_object.hexdigest()
    
    # Return first 16 characters as transaction ID
    return f"txn-{hash_hex[:16]}"


def refund_payment(transaction_id: str, amount: float) -> Dict[str, Any]:
    """
    Mock payment refund function
    
    This would be called if order processing fails after payment.
    Implements the saga pattern for distributed transactions.
    
    In production, this would:
    1. Call payment gateway refund API
    2. Return refund confirmation
    """
    
    print(f"Processing refund for transaction {transaction_id}")
    
    time.sleep(0.1)  # Simulate API call
    
    refund_id = f"ref-{transaction_id[4:]}"  # Remove 'txn-' and add 'ref-'
    
    return {
        'status': 'refunded',
        'refundId': refund_id,
        'originalTransactionId': transaction_id,
        'refundedAt': datetime.utcnow().isoformat() + 'Z',
        'amount': amount,
        'message': 'Payment refunded successfully'
    }


# For local testing
if __name__ == "__main__":
    # Mock event for testing
    test_event = {
        "orderId": "order-test-001",
        "userId": "user-123",
        "items": [
            {
                "productId": "prod-001",
                "quantity": 2,
                "price": 29.99
            }
        ],
        "totalAmount": 59.98,
        "validationResult": {
            "isValid": True,
            "errors": []
        }
    }
    
    # Mock context
    class MockContext:
        request_id = "test-request-123"
        function_name = "test-process-payment"
    
    # Test multiple times to see both success and failure
    print("Testing payment processing (running 5 times):\n")
    for i in range(5):
        print(f"--- Test {i+1} ---")
        try:
            result = lambda_handler(test_event, MockContext())
            print(f"Result: {result['paymentResult']['status']}")
            print(f"Transaction ID: {result['paymentResult']['transactionId']}\n")
        except Exception as e:
            print(f"Payment failed: {str(e)}\n")
