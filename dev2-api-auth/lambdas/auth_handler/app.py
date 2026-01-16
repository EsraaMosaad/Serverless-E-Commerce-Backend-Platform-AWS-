"""
Auth Handler Lambda Function
Developer 2: API & Authentication

Handles user authentication operations including:
- User registration
- User login
- Password management
"""

import json
import os
import boto3
from botocore.exceptions import ClientError

# Initialize AWS clients
cognito_client = boto3.client('cognito-idp')

USER_POOL_ID = os.environ.get('USER_POOL_ID')
USER_POOL_CLIENT_ID = os.environ.get('USER_POOL_CLIENT_ID')


def lambda_handler(event, context):
    """
    Main Lambda handler for authentication operations
    
    Expected event body:
    {
        "action": "register" | "login" | "refresh",
        "email": "user@example.com",
        "password": "password123",
        "name": "User Name" (for registration)
    }
    """
    
    print(f"Received event: {json.dumps(event)}")
    
    try:
        # Parse request body
        body = json.loads(event.get('body', '{}'))
        action = body.get('action', '')
        
        if action == 'register':
            return handle_register(body)
        elif action == 'login':
            return handle_login(body)
        elif action == 'refresh':
            return handle_refresh(body)
        else:
            return response(400, {'error': 'Invalid action. Use: register, login, or refresh'})
    
    except Exception as e:
        print(f"Error: {str(e)}")
        return response(500, {'error': 'Internal server error', 'message': str(e)})


def handle_register(body):
    """Handle user registration"""
    email = body.get('email')
    password = body.get('password')
    name = body.get('name')
    
    if not all([email, password, name]):
        return response(400, {'error': 'Missing required fields: email, password, name'})
    
    try:
        # Create user in Cognito
        response_data = cognito_client.sign_up(
            ClientId=USER_POOL_CLIENT_ID,
            Username=email,
            Password=password,
            UserAttributes=[
                {'Name': 'email', 'Value': email},
                {'Name': 'name', 'Value': name}
            ]
        )
        
        # Automatically confirm the user for a smoother registration flow
        cognito_client.admin_confirm_sign_up(
            UserPoolId=USER_POOL_ID,
            Username=email
        )
        
        return response(201, {
            'message': 'User registered successfully',
            'userId': response_data['UserSub'],
            'email': email
        })
    
    except ClientError as e:
        error_code = e.response['Error']['Code']
        if error_code == 'UsernameExistsException':
            return response(409, {'error': 'User already exists'})
        elif error_code == 'InvalidPasswordException':
            return response(400, {'error': 'Invalid password format'})
        else:
            raise


def handle_login(body):
    """Handle user login"""
    email = body.get('email')
    password = body.get('password')
    
    if not all([email, password]):
        return response(400, {'error': 'Missing required fields: email, password'})
    
    try:
        # Authenticate user
        auth_response = cognito_client.admin_initiate_auth(
            UserPoolId=USER_POOL_ID,
            ClientId=USER_POOL_CLIENT_ID,
            AuthFlow='ADMIN_NO_SRP_AUTH',
            AuthParameters={
                'USERNAME': email,
                'PASSWORD': password
            }
        )
        
        return response(200, {
            'message': 'Login successful',
            'accessToken': auth_response['AuthenticationResult']['AccessToken'],
            'idToken': auth_response['AuthenticationResult']['IdToken'],
            'refreshToken': auth_response['AuthenticationResult']['RefreshToken'],
            'expiresIn': auth_response['AuthenticationResult']['ExpiresIn']
        })
    
    except ClientError as e:
        error_code = e.response['Error']['Code']
        if error_code in ['NotAuthorizedException', 'UserNotFoundException']:
            return response(401, {'error': 'Invalid email or password'})
        else:
            raise


def handle_refresh(body):
    """Handle token refresh"""
    refresh_token = body.get('refreshToken')
    
    if not refresh_token:
        return response(400, {'error': 'Missing refreshToken'})
    
    try:
        auth_response = cognito_client.admin_initiate_auth(
            UserPoolId=USER_POOL_ID,
            ClientId=USER_POOL_CLIENT_ID,
            AuthFlow='REFRESH_TOKEN_AUTH',
            AuthParameters={
                'REFRESH_TOKEN': refresh_token
            }
        )
        
        return response(200, {
            'message': 'Token refreshed successfully',
            'accessToken': auth_response['AuthenticationResult']['AccessToken'],
            'idToken': auth_response['AuthenticationResult']['IdToken'],
            'expiresIn': auth_response['AuthenticationResult']['ExpiresIn']
        })
    
    except ClientError as e:
        return response(401, {'error': 'Invalid or expired refresh token'})


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
