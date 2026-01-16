# Dev1 Backend Core - README

## 🎯 Your Role: Backend Core & Orchestration

As Developer 1, you're responsible for the **heart of the e-commerce backend**:
- **DynamoDB Tables** for data storage (Products, Orders)
- **SQS Queue** for asynchronous order processing
- **SNS Topic** for notifications
- **Step Functions** for order workflow orchestration
- **Lambda Functions** for business logic

## 📁 Directory Structure

```
dev1-backend-core/
├── lambdas/
│   ├── validate_order_handler/
│   │   ├── app.py                 # Order validation logic
│   │   └── requirements.txt       # Python dependencies
│   └── process_payment_handler/
│       ├── app.py                 # Payment processing (mock)
│       └── requirements.txt       # Python dependencies
├── state-machines/
│   └── order-workflow.asl.json    # Step Functions workflow definition
├── STEP_FUNCTIONS_GUIDE.md         # Complete learning guide
├── WORKFLOW_DIAGRAM.md             # Visual workflow documentation
└── README.md                       # This file
```

## 🚀 Quick Start Guide

### Step 1: Understand the Architecture

Read these files in order:
1. **[STEP_FUNCTIONS_GUIDE.md](STEP_FUNCTIONS_GUIDE.md)** - Learn what Step Functions are and how they work
2. **[WORKFLOW_DIAGRAM.md](WORKFLOW_DIAGRAM.md)** - See the visual workflow and data flow

### Step 2: Review the Code

#### Lambda Functions

**Validate Order Handler** (`lambdas/validate_order_handler/app.py`):
- Checks all required fields
- Validates products against database
- Verifies stock and pricing
- Returns validation results

**Process Payment Handler** (`lambdas/process_payment_handler/app.py`):
- Mock payment gateway (90% success rate for testing)
- Generates transaction IDs
- Simulates real payment processing
- Returns payment results

#### Step Functions Workflow

**Order Workflow** (`state-machines/order-workflow.asl.json`):
- Orchestrates the entire order processing
- Calls Lambda functions
- Updates DynamoDB
- Sends SNS notifications
- Handles errors gracefully

### Step 3: Deploy Your Code

```bash
# Navigate to project root
cd c:\Users\HP\Downloads\project-aws-developer\Serverless-E-Commerce-Backend-Platform-AWS-

# Build the application
sam build

# Validate the template
sam validate

# Deploy to AWS
sam deploy --guided
```

Follow the prompts:
- Stack name: `dev-ecommerce-backend`
- AWS Region: Choose your preferred region
- Confirm changes: Y
- Allow SAM CLI IAM role creation: Y

### Step 4: Test the Workflow

#### Option A: AWS Console (Visual)

1. Go to AWS Console → Step Functions
2. Open `dev-OrderProcessingWorkflow`
3. Click **Start execution**
4. Paste this test input:

```json
{
  "orderId": "test-order-001",
  "userId": "test-user-123",
  "items": [
    {
      "productId": "prod-001",
      "quantity": 2,
      "price": 29.99
    }
  ],
  "totalAmount": 59.98
}
```

5. Click **Start execution** and watch it run!

#### Option B: AWS CLI

```bash
# Start execution
aws stepfunctions start-execution \
  --state-machine-arn <your-state-machine-arn> \
  --input file://test-input.json

# Check execution status
aws stepfunctions describe-execution \
  --execution-arn <execution-arn>
```

### Step 5: Monitor and Debug

#### CloudWatch Logs

View Lambda execution logs:
```bash
# Validate Order logs
aws logs tail /aws/lambda/dev-ValidateOrderFunction --follow

# Process Payment logs
aws logs tail /aws/lambda/dev-ProcessPaymentFunction --follow

# Step Functions logs
aws logs tail /aws/states/dev-OrderProcessingWorkflow --follow
```

#### Step Functions Console

1. View execution history
2. See visual workflow with highlighted current state
3. Inspect input/output for each state
4. Check error details if execution fails

## 📚 Learning Path

### Beginner (Start Here)
1. ✅ Read `STEP_FUNCTIONS_GUIDE.md` to understand concepts
2. ✅ Review the Lambda function code with comments
3. ✅ Deploy the application to AWS
4. ✅ Run a test execution and watch it in the console

### Intermediate
5. Modify the validation logic in `validate_order_handler/app.py`
6. Test error scenarios (empty items, invalid products)
7. View error handling in action
8. Customize SNS notification messages

### Advanced
9. Add a new state to the workflow (e.g., send email)
10. Implement real payment gateway integration
11. Add CloudWatch alarms for failed executions
12. Implement saga pattern for rollbacks

## 🔧 Code Explanations

### How Validation Works

```python
# From validate_order_handler/app.py

def validate_required_fields(order):
    """Check if all required fields exist"""
    required_fields = ['orderId', 'userId', 'items', 'totalAmount']
    # Returns list of missing fields
```

This function ensures orders have all necessary data before processing.

### How Payment Works

```python
# From process_payment_handler/app.py

def process_payment(order_id, user_id, amount):
    """Mock payment - 90% success rate"""
    is_successful = random.random() < 0.90
    # In production, this calls real payment API
```

Currently mocked for testing. Replace with Stripe/PayPal in production.

### How Step Functions Orchestrates

```json
{
  "ValidateOrder": {
    "Type": "Task",
    "Resource": "arn:aws:states:::lambda:invoke",
    "Retry": [...],    // Auto-retry on errors
    "Catch": [...],    // Handle failures
    "Next": "ProcessPayment"
  }
}
```

Step Functions automatically handles:
- ✅ Retries with exponential backoff
- ✅ Error catching and routing
- ✅ State transitions
- ✅ Data passing between states

## 🐛 Common Issues & Solutions

### Issue: Lambda times out
**Solution**: Increase timeout in `template.yaml` under `Globals.Function.Timeout`

### Issue: DynamoDB access denied
**Solution**: Check IAM permissions in ValidateOrderFunction policies

### Issue: Step Functions can't invoke Lambda
**Solution**: Verify Lambda ARNs in DefinitionSubstitutions match function names

### Issue: Workflow always fails at payment
**Solution**: This is normal! 10% failure rate is intentional for testing error handling

## 📊 Architecture Overview

```
Customer Order
      ↓
   API Gateway
      ↓
OrderEntryHandler (Dev2)
      ↓
   SQS Queue  ←─── You manage this!
      ↓
 Step Functions ←─── You manage this!
      ↓
  ┌──┴──┐
  ↓     ↓
Lambda  DynamoDB ←─── You manage these!
  ↓
 SNS Topic ←─── You manage this!
```

## 🎓 Resources

- [AWS Step Functions Documentation](https://docs.aws.amazon.com/step-functions/)
- [Amazon States Language Spec](https://states-language.net/)
- [AWS SAM Documentation](https://docs.aws.amazon.com/serverless-application-model/)
- [Python Boto3 Documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/index.html)

## ✅ Checklist: What You've Built

- [x] Order validation Lambda with database checks
- [x] Payment processing Lambda (mock)
- [x] Step Functions workflow with 8 states
- [x] Error handling with Retry and Catch
- [x] DynamoDB integration for order updates
- [x] SNS notifications for success/failure
- [x] Comprehensive logging and monitoring
- [x] SAM template configuration

## 🚀 Next Features to Add

1. **Real Payment Integration**
   - Replace mock with Stripe/PayPal API
   - Add PCI compliance considerations
   - Implement payment method storage

2. **Inventory Management**
   - Reduce stock after successful order
   - Rollback stock on order failure (saga pattern)
   - Add low-stock notifications

3. **Order Tracking**
   - Add more states (Preparing, Shipped, Delivered)
   - Send tracking updates via SNS
   - Add webhook for tracking services

4. **Advanced Error Handling**
   - Dead Letter Queue processing
   - Automated retry with exponential backoff
   - Error analytics dashboard

---

**Need Help?** Check the guide files or AWS documentation. Happy coding! 🎉
