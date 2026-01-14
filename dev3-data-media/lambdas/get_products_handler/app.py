"""
Get Products Handler Lambda Function
Developer 3: Data & Media Management

Retrieves product list from DynamoDB
"""

import json
import os
import boto3
from botocore.exceptions import ClientError
from decimal import Decimal

# Initialize AWS clients
dynamodb = boto3.resource('dynamodb')

PRODUCTS_TABLE = os.environ.get('PRODUCTS_TABLE')
products_table = dynamodb.Table(PRODUCTS_TABLE)


class DecimalEncoder(json.JSONEncoder):
    """Helper class to convert DynamoDB Decimal types to JSON"""
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        return super(DecimalEncoder, self).default(obj)


def lambda_handler(event, context):
    """
    Main Lambda handler for retrieving products
    
    Query parameters:
    - category: Filter by category (optional)
    - limit: Number of items to return (default: 50)
    - lastKey: For pagination (optional)
    """
    
    print(f"Received event: {json.dumps(event)}")
    
    try:
        # Parse query parameters
        params = event.get('queryStringParameters') or {}
        category = params.get('category')
        limit = int(params.get('limit', 50))
        last_key = params.get('lastKey')
        
        # Build scan/query parameters
        scan_params = {
            'Limit': min(limit, 100)  # Cap at 100
        }
        
        # Add pagination token if provided
        if last_key:
            try:
                scan_params['ExclusiveStartKey'] = json.loads(last_key)
            except json.JSONDecodeError:
                return response(400, {'error': 'Invalid lastKey format'})
        
        # Add category filter if provided
        if category:
            scan_params['FilterExpression'] = 'category = :cat'
            scan_params['ExpressionAttributeValues'] = {':cat': category}
        
        # Scan DynamoDB table
        result = products_table.scan(**scan_params)
        
        products = result.get('Items', [])
        last_evaluated_key = result.get('LastEvaluatedKey')
        
        # Build response
        response_body = {
            'products': products,
            'count': len(products),
            'scannedCount': result.get('ScannedCount', 0)
        }
        
        # Add pagination info if there are more items
        if last_evaluated_key:
            response_body['lastKey'] = json.dumps(last_evaluated_key, cls=DecimalEncoder)
            response_body['hasMore'] = True
        else:
            response_body['hasMore'] = False
        
        return response(200, response_body)
    
    except ClientError as e:
        print(f"DynamoDB error: {str(e)}")
        return response(500, {
            'error': 'Database error',
            'message': str(e)
        })
    
    except Exception as e:
        print(f"Error: {str(e)}")
        return response(500, {
            'error': 'Internal server error',
            'message': str(e)
        })


def response(status_code, body):
    """Generate API Gateway response"""
    return {
        'statusCode': status_code,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Headers': 'Content-Type,Authorization',
            'Access-Control-Allow-Methods': 'GET,OPTIONS'
        },
        'body': json.dumps(body, cls=DecimalEncoder)
    }
