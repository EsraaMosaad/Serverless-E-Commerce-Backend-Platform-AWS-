# Developer Guide - 2-Day Hackathon

## Team Organization

### Developer 1: Backend Core & Orchestration
**Working Directory**: `dev1-backend-core/`

#### Responsibilities:
1. ✅ DynamoDB table schemas (already defined in template.yaml)
2. ✅ SQS & SNS configuration (already defined)
3. 🔨 **Step Functions workflow implementation**
   - File: `dev1-backend-core/state-machines/order-workflow.asl.json`
   - Enhance the workflow with:
     - Inventory validation
     - Payment processing integration
     - Error handling and retry logic
     - Compensation logic for failures
4. 🔨 **Database seed data**
   - Create script to populate ProductsTable with initial products
   - Create test orders in OrdersTable

#### Day 1 Tasks:
- [ ] Enhance Step Functions workflow with real business logic
- [ ] Create DynamoDB seed data script (`dev1-backend-core/seed-data.py`)
- [ ] Test Step Functions execution locally
- [ ] Set up CloudWatch alarms for SQS DLQ

#### Day 2 Tasks:
- [ ] Implement error handling in Step Functions
- [ ] Add SNS email subscription for order notifications
- [ ] Create monitoring dashboard
- [ ] Integration testing with Developer 2's order entry

---

### Developer 2: API & Authentication
**Working Directory**: `dev2-api-auth/`

#### Responsibilities:
1. ✅ Cognito User Pool setup (already defined)
2. ✅ API Gateway configuration (already defined)
3. ✅ Auth Handler Lambda (skeleton implemented)
4. ✅ Order Entry Handler Lambda (skeleton implemented)
5. 🔨 **Enhance Lambda functions**

#### Day 1 Tasks:
- [ ] Test and enhance AuthHandler
  - Add email verification
  - Add forgot password flow
  - Add user profile management
- [ ] Enhance OrderEntryHandler
  - Add input validation (joi/pydantic)
  - Add inventory check before queuing
  - Add idempotency (prevent duplicate orders)
- [ ] Create comprehensive error handling
- [ ] Test Cognito integration locally

#### Day 2 Tasks:
- [ ] Add API request validation middleware
- [ ] Implement rate limiting
- [ ] Add comprehensive logging
- [ ] Create Postman collection for testing
- [ ] Integration testing with Developer 3's endpoints

#### Lambda Enhancement Examples:

**Validation in OrderEntryHandler**:
```python
from pydantic import BaseModel, validator

class OrderItem(BaseModel):
    productId: str
    quantity: int
    
    @validator('quantity')
    def quantity_positive(cls, v):
        if v <= 0:
            raise ValueError('Quantity must be positive')
        return v
```

---

### Developer 3: Data & Media Management
**Working Directory**: `dev3-data-media/`

#### Responsibilities:
1. ✅ S3 bucket configuration (already defined)
2. ✅ Get Products Handler (skeleton implemented)
3. ✅ Upload URL Handler (skeleton implemented)
4. 🔨 **Enhance Lambda functions**

#### Day 1 Tasks:
- [ ] Enhance GetProductsHandler
  - Add search functionality (by name, description)
  - Add sorting options
  - Optimize DynamoDB queries
  - Add response caching headers
- [ ] Enhance UploadUrlHandler
  - Add image size validation
  - Generate thumbnails using Lambda layers
  - Store image metadata in DynamoDB
- [ ] Create product management endpoints
  - POST /products (create product)
  - PUT /products/{id} (update product)
  - DELETE /products/{id} (soft delete)

#### Day 2 Tasks:
- [ ] Implement CloudFront distribution for S3
- [ ] Add image optimization Lambda
- [ ] Create product search index
- [ ] Bulk import script for products
- [ ] Integration testing with complete flow

#### New Endpoints to Add:

**POST /products** (Create Product):
```python
# dev3-data-media/lambdas/create_product_handler/app.py

def lambda_handler(event, context):
    body = json.loads(event['body'])
    
    product_id = str(uuid.uuid4())
    product = {
        'productId': product_id,
        'name': body['name'],
        'description': body.get('description', ''),
        'price': Decimal(str(body['price'])),
        'category': body['category'],
        'imageUrl': body.get('imageUrl'),
        'inStock': True,
        'stock': body.get('stock', 0),
        'createdAt': datetime.utcnow().isoformat(),
        'updatedAt': datetime.utcnow().isoformat()
    }
    
    products_table.put_item(Item=product)
    
    return response(201, product)
```

---

## Parallel Development Strategy

### Merge Conflict Prevention

1. **Each developer owns their directory**
   - No cross-directory edits without coordination
   - Communicate before modifying shared resources

2. **template.yaml modifications**
   - Create separate branches for infrastructure changes
   - Coordinate via team chat before editing
   - Use feature toggles for experimental resources

3. **Shared utilities**
   - Place in `shared/layers/common/`
   - Document all changes
   - Version shared code

### Communication Checkpoints

**Morning Standup** (15 min):
- What did I complete yesterday?
- What am I working on today?
- Any blockers?

**Midday Sync** (10 min):
- Progress check
- Resolve any integration issues
- Update task board

**End-of-Day Review** (15 min):
- Demo completed features
- Plan next day
- Commit and push code

---

## Testing Strategy

### Unit Tests
Each developer tests their own functions:

```bash
# Create test file
# tests/test_dev1.py
# tests/test_dev2.py
# tests/test_dev3.py

pytest tests/test_dev2.py -v
```

### Integration Tests
Test cross-module functionality:

```bash
# Full flow test: Register → Login → Create Order → Process Order
pytest tests/test_integration.py -v
```

### Local Testing
```bash
# Start local API
sam local start-api

# Test in another terminal
curl http://localhost:3000/products
```

---

## Git Workflow

### Branch Strategy
```bash
# Main branch
main

# Developer branches
dev1-backend-core
dev2-api-auth
dev3-data-media

# Feature branches
feature/dev2-auth-enhancements
feature/dev3-product-search
```

### Daily Workflow
```bash
# Morning: Pull latest changes
git checkout dev2-api-auth
git pull origin main
git merge main

# Work on features
git add .
git commit -m "feat: add order validation"
git push origin dev2-api-auth

# End of day: Merge to main (if stable)
git checkout main
git merge dev2-api-auth
git push origin main
```

---

## Debugging Tips

### Lambda Debugging
```python
# Add detailed logging
import logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event, context):
    logger.info(f"Event: {json.dumps(event)}")
    logger.info(f"Context: {context}")
    # ... your code
```

### DynamoDB Debugging
```bash
# List tables
aws dynamodb list-tables

# Scan table
aws dynamodb scan --table-name dev-ProductsTable

# Get specific item
aws dynamodb get-item \
  --table-name dev-ProductsTable \
  --key '{"productId": {"S": "prod-123"}}'
```

### API Gateway Debugging
```bash
# Enable CloudWatch logs for API Gateway
# In template.yaml, add:
# MethodSettings:
#   - ResourcePath: '/*'
#     HttpMethod: '*'
#     LoggingLevel: INFO
```

---

## Performance Optimization

### Lambda
- Right-size memory (256MB default, adjust per function)
- Use Lambda Layers for shared dependencies
- Implement connection pooling for DynamoDB
- Enable X-Ray tracing

### DynamoDB
- Use PAY_PER_REQUEST for variable workloads
- Add GSIs only when needed
- Use batch operations for bulk writes
- Implement caching with DAX (optional)

### API Gateway
- Enable response caching (for GET /products)
- Implement request throttling
- Use API keys for partner access

---

## Security Checklist

- ✅ Use HTTPS only
- ✅ Cognito for authentication
- ✅ IAM least privilege policies
- ⬜ Input validation on all endpoints
- ⬜ SQL injection prevention (use parameterized queries)
- ⬜ XSS prevention (sanitize inputs)
- ⬜ CORS properly configured
- ⬜ API rate limiting
- ⬜ Secrets in Secrets Manager (not environment variables)

---

## Hackathon Demo Preparation

### Demo Script (Day 2 Afternoon)

1. **Architecture Overview** (2 min)
   - Show template.yaml structure
   - Explain serverless benefits

2. **User Registration & Login** (3 min)
   ```bash
   # Live demo with Postman
   POST /auth (register)
   POST /auth (login)
   ```

3. **Product Catalog** (3 min)
   ```bash
   GET /products
   GET /products/upload (show pre-signed URL)
   # Upload image demo
   ```

4. **Order Processing** (5 min)
   ```bash
   POST /orders
   # Show SQS queue
   # Show Step Functions execution
   # Show SNS notification
   ```

5. **Monitoring** (2 min)
   - CloudWatch dashboard
   - Lambda logs
   - DynamoDB metrics

### Deploy Before Demo
```bash
# 30 minutes before demo
sam build && sam deploy

# Verify all endpoints
./scripts/verify-deployment.sh
```

---

## Troubleshooting Common Issues

### Issue: Lambda timeout
**Solution**: Increase timeout in template.yaml (max 900s)

### Issue: DynamoDB throttling
**Solution**: Using PAY_PER_REQUEST mode eliminates this

### Issue: CORS errors
**Solution**: Already configured in template.yaml

### Issue: Cognito token expired
**Solution**: Use refresh token flow

### Issue: S3 upload fails
**Solution**: Check pre-signed URL expiration and content-type

---

## Resources

- [AWS SAM Documentation](https://docs.aws.amazon.com/serverless-application-model/)
- [AWS Lambda Best Practices](https://docs.aws.amazon.com/lambda/latest/dg/best-practices.html)
- [DynamoDB Best Practices](https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/best-practices.html)
- [API Gateway CORS](https://docs.aws.amazon.com/apigateway/latest/developerguide/how-to-cors.html)
- [Step Functions ASL](https://states-language.net/spec.html)

---

## Quick Commands Reference

```bash
# Validate template
sam validate

# Build project
sam build

# Deploy (first time)
sam deploy --guided

# Deploy (subsequent)
sam deploy

# Local API
sam local start-api

# Invoke function locally
sam local invoke FunctionName -e events/event.json

# View logs
sam logs -n FunctionName --tail

# Delete stack
sam delete
```

Good luck with your hackathon! 🚀
