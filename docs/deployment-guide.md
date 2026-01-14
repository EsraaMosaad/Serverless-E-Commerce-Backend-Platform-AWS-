# Deployment Guide

## Prerequisites

1. **AWS Account**: Ensure you have an AWS account with appropriate permissions
2. **AWS CLI**: Install and configure AWS CLI
   ```bash
   aws configure
   ```
3. **AWS SAM CLI**: Install SAM CLI
   ```bash
   pip install aws-sam-cli
   ```
4. **Python 3.9**: Ensure Python 3.9 is installed

## Initial Setup

### 1. Validate the Template
```bash
sam validate
```

### 2. Build the Application
```bash
sam build
```

This will:
- Download dependencies for each Lambda function
- Prepare deployment artifacts
- Validate code and templates

### 3. Deploy to AWS (First Time)
```bash
sam deploy --guided
```

You'll be prompted for:
- **Stack Name**: e.g., `ecommerce-serverless-dev`
- **AWS Region**: e.g., `us-east-1`
- **Parameter Environment**: `dev` (or `staging`, `prod`)
- **Confirm changes**: Review the changeset
- **Allow SAM CLI IAM role creation**: Yes
- **Save arguments to configuration**: Yes

### 4. Subsequent Deployments
After the first guided deployment:
```bash
sam build && sam deploy
```

## Local Development & Testing

### Start API Gateway Locally
```bash
sam local start-api
```

This starts a local API at `http://127.0.0.1:3000`

### Invoke Individual Functions
```bash
# Test Auth Handler
sam local invoke AuthHandler -e events/auth-register.json

# Test GetProducts
sam local invoke GetProductsHandler -e events/get-products.json

# Test OrderEntry
sam local invoke OrderEntryHandler -e events/create-order.json
```

### Generate Test Events
Create test event files in `events/` directory:

**events/auth-register.json**:
```json
{
  "body": "{\"action\":\"register\",\"email\":\"test@example.com\",\"password\":\"Test123!\",\"name\":\"Test User\"}"
}
```

## Environment-Specific Deployments

### Deploy to Staging
```bash
sam build && sam deploy --config-env staging
```

### Deploy to Production
```bash
sam build && sam deploy --config-env prod
```

## Post-Deployment

### Get Stack Outputs
```bash
aws cloudformation describe-stacks \
  --stack-name ecommerce-serverless-dev \
  --query 'Stacks[0].Outputs' \
  --output table
```

### Test the Deployed API
```bash
# Get API URL from outputs
API_URL=$(aws cloudformation describe-stacks \
  --stack-name ecommerce-serverless-dev \
  --query 'Stacks[0].Outputs[?OutputKey==`ApiUrl`].OutputValue' \
  --output text)

# Test GET products
curl -X GET "${API_URL}products"

# Test POST auth/register
curl -X POST "${API_URL}auth" \
  -H "Content-Type: application/json" \
  -d '{"action":"register","email":"test@example.com","password":"Test123!","name":"Test User"}'
```

## Monitoring & Debugging

### View Logs
```bash
# Get logs for a specific function
sam logs -n GetProductsHandler --stack-name ecommerce-serverless-dev --tail

# View logs from specific time
sam logs -n GetProductsHandler --stack-name ecommerce-serverless-dev --start-time '10min ago'
```

### CloudWatch Logs
Navigate to AWS CloudWatch Console:
- Log Groups: `/aws/lambda/<FunctionName>`
- Step Functions: `/aws/vendedlogs/states/OrderProcessingWorkflow`

## Cleanup

### Delete the Stack
```bash
sam delete --stack-name ecommerce-serverless-dev
```

**Warning**: This will delete all resources including:
- DynamoDB tables (and all data)
- S3 bucket (must be empty first)
- Lambda functions
- API Gateway
- All other resources

### Empty S3 Bucket Before Deletion
```bash
BUCKET_NAME=$(aws cloudformation describe-stacks \
  --stack-name ecommerce-serverless-dev \
  --query 'Stacks[0].Outputs[?OutputKey==`ProductImagesBucketName`].OutputValue' \
  --output text)

aws s3 rm s3://${BUCKET_NAME} --recursive
```

## Troubleshooting

### Build Failures
```bash
# Clean and rebuild
rm -rf .aws-sam
sam build --use-container
```

### Deployment Failures
- Check IAM permissions
- Verify AWS CLI is configured correctly
- Check CloudFormation events in AWS Console

### Function Errors
- Check CloudWatch Logs
- Verify environment variables
- Test locally with `sam local invoke`

## Security Best Practices

1. **Use Secrets Manager**: Store sensitive data (API keys, passwords) in AWS Secrets Manager
2. **Enable VPC**: For production, deploy Lambdas in VPC
3. **Enable WAF**: Protect API Gateway with AWS WAF
4. **Enable CloudTrail**: Audit all API calls
5. **Implement Rate Limiting**: Use API Gateway throttling
6. **Use HTTPS Only**: Already configured in template

## Cost Optimization

1. **DynamoDB**: Using PAY_PER_REQUEST billing mode
2. **Lambda**: Right-size memory allocation (currently 256MB)
3. **API Gateway**: Monitor request counts
4. **S3**: Implement lifecycle policies for old images
5. **CloudWatch Logs**: Set retention periods

## Next Steps

1. Implement comprehensive unit tests
2. Add integration tests
3. Set up CI/CD pipeline (GitHub Actions, CodePipeline)
4. Configure custom domain for API Gateway
5. Implement observability (X-Ray tracing)
6. Add API documentation (Swagger/OpenAPI)
