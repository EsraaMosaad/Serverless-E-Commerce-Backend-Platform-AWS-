"""
Validate Order Handler - Step Functions Task
Developer 1: Backend Core & Orchestration

This Lambda function validates incoming orders before processing.
It checks:
1. Required fields are present
2. Products exist in the database
3. Order amounts are correct

This function is called by Step Functions as part of the order workflow.
"""

import json
import os
import boto3
from decimal import Decimal
from typing import Dict, Any, List

# Initialize AWS clients
dynamodb = boto3.resource('dynamodb')
products_table = dynamodb.Table(os.environ['PRODUCTS_TABLE'])

# Custom JSON encoder to handle Decimal types from DynamoDB
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
        "items": [
            {"productId": "prod-1", "quantity": 2, "price": 29.99}
        ],
        "totalAmount": 59.98
    }
    
    Output (to Step Functions):
    {
        "orderId": "order-123",
        "userId": "user-456",
        "items": [...],
        "totalAmount": 59.98,
        "validationResult": {
            "isValid": true/false,
            "errors": [...],
            "validatedAt": "2024-01-16T10:00:00Z"
        }
    }
    """
    
    print(f"Received order validation request: {json.dumps(event, cls=DecimalEncoder)}")
    
    try:
        # Step 1: Validate required fields
        validation_errors = validate_required_fields(event)
        
        if not validation_errors:
            # Step 2: Validate items against product database
            item_errors = validate_items(event.get('items', []))
            validation_errors.extend(item_errors)
        
        if not validation_errors:
            # Step 3: Validate total amount calculation
            amount_errors = validate_total_amount(event)
            validation_errors.extend(amount_errors)
        
        # Build response
        is_valid = len(validation_errors) == 0
        
        response = {
            **event,  # Include all original fields
            'validationResult': {
                'isValid': is_valid,
                'errors': validation_errors,
                'validatedAt': context.request_id,
                'validatedBy': context.function_name
            }
        }
        
        if is_valid:
            print(f"✅ Order {event.get('orderId')} validated successfully")
        else:
            print(f"❌ Order {event.get('orderId')} validation failed: {validation_errors}")
            # Raise exception so Step Functions can catch it
            raise ValueError(f"Order validation failed: {', '.join(validation_errors)}")
        
        return response
        
    except Exception as e:
        print(f"Error validating order: {str(e)}")
        raise


def validate_required_fields(order: Dict[str, Any]) -> List[str]:
    """
    Check that all required fields are present in the order
    
    Required fields:
    - orderId: Unique order identifier
    - userId: Customer identifier
    - items: Array of order items
    - totalAmount: Total order amount
    """
    errors = []
    required_fields = ['orderId', 'userId', 'items', 'totalAmount']
    
    for field in required_fields:
        if field not in order or order[field] is None:
            errors.append(f"Missing required field: {field}")
    
    # Validate items is an array and not empty
    if 'items' in order:
        if not isinstance(order['items'], list):
            errors.append("Items must be an array")
        elif len(order['items']) == 0:
            errors.append("Order must contain at least one item")
    
    return errors


def validate_items(items: List[Dict[str, Any]]) -> List[str]:
    """
    Validate each item in the order
    Checks:
    1. Product exists in database
    2. Quantity is valid
    3. Price matches database
    """
    errors = []
    
    for idx, item in enumerate(items):
        item_num = idx + 1
        
        # Check required item fields
        if 'productId' not in item:
            errors.append(f"Item {item_num}: Missing productId")
            continue
            
        if 'quantity' not in item:
            errors.append(f"Item {item_num}: Missing quantity")
            continue
            
        # Validate quantity
        try:
            quantity = int(item['quantity'])
            if quantity <= 0:
                errors.append(f"Item {item_num}: Quantity must be positive")
        except (ValueError, TypeError):
            errors.append(f"Item {item_num}: Invalid quantity")
            continue
        
        # Check product exists in database
        try:
            response = products_table.get_item(
                Key={'productId': item['productId']}
            )
            
            if 'Item' not in response:
                errors.append(f"Item {item_num}: Product {item['productId']} not found")
                continue
            
            product = response['Item']
            
            # Check stock availability (if tracked)
            if 'stock' in product:
                available_stock = int(product['stock'])
                if available_stock < quantity:
                    errors.append(
                        f"Item {item_num}: Insufficient stock for {item['productId']} "
                        f"(requested: {quantity}, available: {available_stock})"
                    )
            
            # Validate price (if provided in order)
            if 'price' in item:
                db_price = float(product.get('price', 0))
                order_price = float(item['price'])
                
                # Allow small floating point differences
                if abs(db_price - order_price) > 0.01:
                    errors.append(
                        f"Item {item_num}: Price mismatch for {item['productId']} "
                        f"(expected: {db_price}, received: {order_price})"
                    )
                    
        except Exception as e:
            print(f"Error validating product {item['productId']}: {str(e)}")
            errors.append(f"Item {item_num}: Error validating product - {str(e)}")
    
    return errors


def validate_total_amount(order: Dict[str, Any]) -> List[str]:
    """
    Validate that the total amount matches the sum of item prices
    """
    errors = []
    
    try:
        calculated_total = 0.0
        
        for item in order.get('items', []):
            if 'price' in item and 'quantity' in item:
                price = float(item['price'])
                quantity = int(item['quantity'])
                calculated_total += price * quantity
        
        order_total = float(order.get('totalAmount', 0))
        
        # Allow small floating point differences (1 cent)
        if abs(calculated_total - order_total) > 0.01:
            errors.append(
                f"Total amount mismatch: expected {calculated_total:.2f}, "
                f"received {order_total:.2f}"
            )
            
    except Exception as e:
        errors.append(f"Error calculating total: {str(e)}")
    
    return errors


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
        "totalAmount": 59.98
    }
    
    # Mock context
    class MockContext:
        request_id = "test-request-123"
        function_name = "test-validate-order"
    
    result = lambda_handler(test_event, MockContext())
    print(json.dumps(result, indent=2, cls=DecimalEncoder))
