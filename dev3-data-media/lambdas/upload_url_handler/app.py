"""
Upload URL Handler Lambda Function
Developer 3: Data & Media Management

Generates S3 pre-signed URLs for product image uploads
"""

import json
import os
import uuid
from datetime import datetime
import boto3
from botocore.exceptions import ClientError

# Initialize AWS clients
s3_client = boto3.client('s3')

PRODUCT_IMAGES_BUCKET = os.environ.get('PRODUCT_IMAGES_BUCKET')


def lambda_handler(event, context):
    """
    Main Lambda handler for generating S3 pre-signed URLs
    
    Query parameters:
    - filename: Original filename (optional)
    - contentType: MIME type (default: image/jpeg)
    - expiresIn: URL validity in seconds (default: 300, max: 3600)
    """
    
    print(f"Received event: {json.dumps(event)}")
    
    try:
        # Parse query parameters
        params = event.get('queryStringParameters') or {}
        filename = params.get('filename', f'product-{uuid.uuid4()}.jpg')
        content_type = params.get('contentType', 'image/jpeg')
        expires_in = min(int(params.get('expiresIn', 300)), 3600)  # Max 1 hour
        
        # Validate content type (only allow images)
        allowed_types = [
            'image/jpeg',
            'image/jpg',
            'image/png',
            'image/gif',
            'image/webp'
        ]
        
        if content_type not in allowed_types:
            return response(400, {
                'error': 'Invalid content type',
                'allowedTypes': allowed_types
            })
        
        # Generate unique key for S3
        timestamp = datetime.utcnow().strftime('%Y%m%d')
        file_extension = filename.split('.')[-1] if '.' in filename else 'jpg'
        s3_key = f'products/{timestamp}/{uuid.uuid4()}.{file_extension}'
        
        # Generate pre-signed URL for PUT operation
        presigned_url = s3_client.generate_presigned_url(
            'put_object',
            Params={
                'Bucket': PRODUCT_IMAGES_BUCKET,
                'Key': s3_key,
                'ContentType': content_type,
                'Metadata': {
                    'originalFilename': filename,
                    'uploadedAt': datetime.utcnow().isoformat()
                }
            },
            ExpiresIn=expires_in,
            HttpMethod='PUT'
        )
        
        # Generate the public URL (for reference, not for direct access)
        file_url = f"https://{PRODUCT_IMAGES_BUCKET}.s3.amazonaws.com/{s3_key}"
        
        return response(200, {
            'uploadUrl': presigned_url,
            'fileUrl': file_url,
            'key': s3_key,
            'expiresIn': expires_in,
            'expiresAt': (datetime.utcnow().timestamp() + expires_in),
            'instructions': {
                'method': 'PUT',
                'headers': {
                    'Content-Type': content_type
                },
                'note': 'Upload the file directly to the uploadUrl using PUT method'
            }
        })
    
    except ClientError as e:
        print(f"S3 error: {str(e)}")
        return response(500, {
            'error': 'Failed to generate upload URL',
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
        'body': json.dumps(body)
    }
