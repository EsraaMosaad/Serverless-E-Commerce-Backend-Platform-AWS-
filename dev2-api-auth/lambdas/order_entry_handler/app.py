"""
Order Entry Handler Lambda Function
Developer 2: API & Authentication

Receives new order requests and queues them for processing via SQS
"""

import json
import os
import uuid
from datetime import datetime
import boto3
from botocore.exceptions import ClientError

# Initialize AWS clients
sqs_client = boto3.client('sqs')
dynamodb = boto3.resource('dynamodb')

ORDER_QUEUE_URL = os.environ.get('ORDER_QUEUE_URL')
PRODUCTS_TABLE = os.environ.get('PRODUCTS_TABLE')

products_table = dynamodb.Table(PRODUCTS_TABLE)


def lambda_handler(event, context):
    """
    Main Lambda handler for order entry
    
    Expected event body:
    {
        "userId": "user-123",
        "items": [
            {
                "productId": "prod-1",
                "quantity": 2
            }
        ],
        "shippingAddress": {
            "street": "123 Main St",
            "city": "Boston",
            "state": "MA",
            "zip": "02101"
        }
    }
    """
    
    print(f"Received event: {json.dumps(event)}")
    
    try:
        # Parse request body
        body = json.loads(event.get('body', '{}'))
        
        # Extract user ID from Cognito authorizer context
        user_id = extract_user_id(event)
        
        # Validate required fields
        items = body.get('items', [])
        shipping_address = body.get('shippingAddress', {})
        
        if not items:
            return response(400, {'error': 'Order must contain at least one item'})
        
        if not shipping_address:
            return response(400, {'error': 'Shipping address is required'})
        
        # Validate products exist (basic check)
        total_amount = 0.0
        for item in items:
            product_id = item.get('productId')
            quantity = item.get('quantity', 0)
            
            if not product_id or quantity <= 0:
                return response(400, {'error': 'Invalid item in order'})
            
            # Check if product exists (placeholder - implement actual price lookup)
            try:
                product = products_table.get_item(Key={'productId': product_id})
                if 'Item' not in product:
                    return response(404, {'error': f'Product {product_id} not found'})
                
                # Calculate total (assuming product has 'price' field)
                price = float(product['Item'].get('price', 0))
                total_amount += price * quantity
            except Exception as e:
                print(f"Error fetching product {product_id}: {str(e)}")
                # Continue for hackathon - in production, fail immediately
        
        # Create order object
        order_id = str(uuid.uuid4())
        order = {
            'orderId': order_id,
            'userId': user_id,
            'items': items,
            'shippingAddress': shipping_address,
            'totalAmount': total_amount,
            'status': 'PENDING',
            'createdAt': datetime.utcnow().isoformat(),
            'updatedAt': datetime.utcnow().isoformat()
        }
        
        # Send order to SQS for processing
        sqs_response = sqs_client.send_message(
            QueueUrl=ORDER_QUEUE_URL,
            MessageBody=json.dumps(order),
            MessageAttributes={
                'orderId': {
                    'StringValue': order_id,
                    'DataType': 'String'
                },
                'userId': {
                    'StringValue': user_id,
                    'DataType': 'String'
                }
            }
        )
        
        print(f"Order {order_id} sent to SQS: {sqs_response['MessageId']}")
        
        return response(201, {
            'message': 'Order created successfully',
            'orderId': order_id,
            'status': 'PENDING',
            'totalAmount': total_amount,
            'sqsMessageId': sqs_response['MessageId']
        })
    
    except Exception as e:
        print(f"Error: {str(e)}")
        return response(500, {'error': 'Internal server error', 'message': str(e)})


def extract_user_id(event):
    """Extract user ID from API Gateway authorizer context"""
    try:
        # From Cognito authorizer
        claims = event['requestContext']['authorizer']['claims']
        return claims.get('sub', 'anonymous')
    except (KeyError, TypeError):
        # Fallback for testing without auth
        body = json.loads(event.get('body', '{}'))
        return body.get('userId', 'test-user')


def response(status_code, body):
    """Generate API Gateway response"""
    return {
        'statusCode': status_code,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Headers': 'Content-Type,Authorization',
            'Access-Control-Allow-Methods': 'POST,OPTIONS'
        },
        'body': json.dumps(body)
    }
