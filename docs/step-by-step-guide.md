# 📚 E-Commerce Serverless SAM - Step-by-Step Understanding Guide

Welcome! This guide will walk you through understanding this e-commerce serverless backend project step by step.

---

## 🎯 **Step 1: Project Overview**

### What is this project?
This is a **serverless e-commerce backend** built using **AWS SAM (Serverless Application Model)**. It's designed for a **2-day hackathon** with **3 developers** working in parallel.

### Key Technologies:
- **AWS SAM** - Infrastructure as Code framework for serverless apps
- **AWS Lambda** - Serverless compute (Python 3.9)
- **API Gateway** - REST API endpoints
- **DynamoDB** - NoSQL database for products and orders
- **Cognito** - User authentication
- **SQS** - Message queuing for async processing
- **SNS** - Notifications
- **Step Functions** - Workflow orchestration
- **S3** - File storage for product images

### Why Serverless?
- ✅ **No server management** - AWS handles infrastructure
- ✅ **Auto-scaling** - Scales automatically with demand
- ✅ **Pay-per-use** - Only pay for what you use
- ✅ **High availability** - Built-in redundancy

---

## 📂 **Step 2: Project Structure**

The project is organized by **developer responsibilities**:

```
ecommerce-serverless-sam/
├── template.yaml                # Master infrastructure definition
├── dev1-backend-core/          # Developer 1's workspace
├── dev2-api-auth/              # Developer 2's workspace (YOU ARE HERE!)
├── dev3-data-media/            # Developer 3's workspace
├── shared/                     # Shared code/utilities
├── tests/                      # Test files
└── docs/                       # Documentation
```

### Your Current File
You're looking at: `dev2-api-auth/lambdas/auth_handler/app.py`
- This is **Developer 2's** authentication Lambda function
- It handles user registration, login, and token refresh

---

## 👥 **Step 3: Developer Assignments**

### **Developer 1: Backend Core & Orchestration** 🔵
**Focus**: Database, Message Queues, Workflows

**Responsibilities**:
1. **ProductsTable** (DynamoDB) - Stores product catalog
2. **OrdersTable** (DynamoDB) - Stores customer orders
3. **OrderProcessingQueue** (SQS) - Queues orders for async processing
4. **OrderCompletedTopic** (SNS) - Sends notifications when orders complete
5. **OrderProcessingWorkflow** (Step Functions) - Orchestrates order processing

**Directory**: `dev1-backend-core/`

---

### **Developer 2: API & Authentication** 🟢 ⭐ **(YOUR AREA!)**
**Focus**: User management, API endpoints for authentication and orders

**Responsibilities**:
1. **UserPool** (Cognito) - Manages user accounts
2. **ECommerceApi** (API Gateway) - Exposes REST API endpoints
3. **AuthHandler** (Lambda) - Handles register/login/refresh
4. **OrderEntryHandler** (Lambda) - Creates new orders

**Directory**: `dev2-api-auth/`

**Your API Endpoints**:
- `POST /auth` - User authentication (public, no auth required)
- `POST /orders` - Create orders (requires authentication)

---

### **Developer 3: Data & Media Management** 🟣
**Focus**: Product data and image uploads

**Responsibilities**:
1. **ProductImagesBucket** (S3) - Stores product images
2. **GetProductsHandler** (Lambda) - Retrieves product listings
3. **UploadUrlHandler** (Lambda) - Generates secure upload URLs

**Directory**: `dev3-data-media/`

**Their API Endpoints**:
- `GET /products` - List products (public)
- `GET /products/upload` - Get upload URL (requires auth)

---

## 🔄 **Step 4: How the System Works**

### Architecture Flow Diagram:

```
User → API Gateway → Lambda Functions → AWS Services
                          ↓
                    ┌─────┴─────┐
                    ↓           ↓
                Cognito    DynamoDB
                    ↓           ↓
                   Auth     Products/Orders
                              ↓
                            SQS Queue
                              ↓
                        Step Functions
                              ↓
                         SNS Topic
```

### Example: User Registration Flow (Your Code!)

1. **User sends request**: `POST /auth` with email, password, name
2. **API Gateway** receives request
3. **AuthHandler Lambda** (your code) is invoked
4. **Lambda calls Cognito** to create user
5. **Cognito** stores user credentials securely
6. **Response** sent back to user

### Example: Creating an Order Flow

1. **User logs in** → Gets JWT token from `/auth`
2. **User sends**: `POST /orders` with JWT token in header
3. **API Gateway** validates JWT with Cognito
4. **OrderEntryHandler Lambda** validates order items
5. **Lambda sends message** to SQS Queue
6. **Step Functions** picks up message from queue
7. **Step Functions** processes payment, updates database
8. **SNS** sends notification when complete

---

## 💻 **Step 5: Understanding Your Code (dev2-api-auth)**

### File: `auth_handler/app.py` (Currently Open)

Let's break down what this code does:

#### Main Handler Function:
```python
def lambda_handler(event, context):
    # Entry point for Lambda
    # Receives HTTP requests from API Gateway
    # Routes to appropriate handler based on "action"
```

#### Three Actions Supported:

1. **Register** (`handle_register`)
   - Creates new user in Cognito
   - Input: email, password, name
   - Output: userId, email

2. **Login** (`handle_login`)
   - Authenticates existing user
   - Input: email, password
   - Output: accessToken, idToken, refreshToken

3. **Refresh** (`handle_refresh`)
   - Refreshes expired access token
   - Input: refreshToken
   - Output: new accessToken, idToken

#### Key Environment Variables:
- `USER_POOL_ID` - Which Cognito pool to use
- `USER_POOL_CLIENT_ID` - App client ID for API calls

---

## 🗂️ **Step 6: Understanding the Template (template.yaml)**

The `template.yaml` file defines **ALL infrastructure** using code. Here's what it contains:

### Global Settings (Lines 8-19):
```yaml
Globals:
  Function:
    Runtime: python3.9      # All Lambdas use Python 3.9
    Timeout: 30             # Max execution time
    MemorySize: 256         # Memory allocation
```

### Resources - Your Section (Lines 188-314):

#### 1. **Cognito User Pool** (Lines 189-215)
- Manages user accounts
- Requires email verification
- Password policy: 8 chars, uppercase, lowercase, numbers, symbols

#### 2. **API Gateway** (Lines 231-248)
- Creates REST API
- Enables CORS (Cross-Origin Resource Sharing)
- Uses Cognito for authentication

#### 3. **AuthHandler Lambda** (Lines 251-283)
- Points to your `dev2-api-auth/lambdas/auth_handler/` code
- Has permissions to interact with Cognito
- Endpoint: `POST /auth` (no authentication required)

#### 4. **OrderEntryHandler Lambda** (Lines 286-314)
- Creates new orders
- Sends messages to SQS queue
- Endpoint: `POST /orders` (authentication required)

---

## 🔐 **Step 7: Authentication Flow in Detail**

### How Cognito Authentication Works:

```
┌──────────┐    ┌──────────┐    ┌──────────┐
│  Client  │───▶│ AuthHandler│───▶│ Cognito  │
│ (Browser)│    │  Lambda    │    │UserPool  │
└──────────┘    └──────────┘    └──────────┘
     │                │                │
     │  POST /auth    │                │
     │  (register)    │                │
     ├───────────────▶│                │
     │                │ CreateUser     │
     │                ├───────────────▶│
     │                │                │
     │                │   UserSub      │
     │                │◀───────────────┤
     │  User Created  │                │
     │◀───────────────┤                │
     │                │                │
     │  POST /auth    │                │
     │  (login)       │                │
     ├───────────────▶│                │
     │                │ Authenticate   │
     │                ├───────────────▶│
     │                │                │
     │                │ JWT Tokens     │
     │                │◀───────────────┤
     │  Tokens        │                │
     │◀───────────────┤                │
```

### Token Types:

1. **Access Token** - Short-lived (1 hour), used for API calls
2. **ID Token** - Contains user information
3. **Refresh Token** - Long-lived, used to get new access tokens

---

## 📊 **Step 8: Database Schema**

### ProductsTable (DynamoDB)
```
Primary Key: productId (String)

Example Item:
{
  "productId": "prod-001",
  "name": "Laptop",
  "price": 999.99,
  "description": "High-performance laptop",
  "imageUrl": "https://s3.../laptop.jpg",
  "stock": 50
}
```

### OrdersTable (DynamoDB)
```
Primary Key: orderId (String)
GSI: UserOrdersIndex (userId + createdAt)

Example Item:
{
  "orderId": "order-001",
  "userId": "user-123",
  "items": [
    {"productId": "prod-001", "quantity": 2, "price": 999.99}
  ],
  "totalAmount": 1999.98,
  "status": "processing",
  "createdAt": "2026-01-14T09:00:00Z"
}
```

---

## 🚀 **Step 9: How to Work with This Project**

### Local Development:

#### 1. **Validate the Template**
```bash
cd /home/esraaabdelrazek/.gemini/antigravity/scratch/ecommerce-serverless-sam
sam validate
```

#### 2. **Build the Project**
```bash
sam build
```
This packages all Lambda functions and their dependencies.

#### 3. **Test Locally**
```bash
sam local start-api
```
Starts a local API Gateway on `http://localhost:3000`

#### 4. **Test Your Auth Handler**
```bash
# Register a user
curl -X POST http://localhost:3000/auth \
  -H "Content-Type: application/json" \
  -d '{
    "action": "register",
    "email": "test@example.com",
    "password": "Test123!",
    "name": "Test User"
  }'

# Login
curl -X POST http://localhost:3000/auth \
  -H "Content-Type: application/json" \
  -d '{
    "action": "login",
    "email": "test@example.com",
    "password": "Test123!"
  }'
```

#### 5. **Deploy to AWS**
```bash
sam deploy --guided
```
Follow the prompts to deploy to your AWS account.

---

## 🔍 **Step 10: Understanding the Files in Your Directory**

### Your Directory Structure:
```
dev2-api-auth/
├── lambdas/
│   ├── auth_handler/
│   │   ├── app.py              ← You're looking at this!
│   │   └── requirements.txt    ← Python dependencies
│   └── order_entry_handler/
│       ├── app.py              ← Creates orders
│       └── requirements.txt
```

### What Each File Does:

#### `auth_handler/app.py`
- **Purpose**: User authentication
- **Functions**:
  - `lambda_handler()` - Main entry point
  - `handle_register()` - Create new users
  - `handle_login()` - Authenticate users
  - `handle_refresh()` - Refresh access tokens
  - `response()` - Format API responses

#### `auth_handler/requirements.txt`
```
boto3>=1.26.0
botocore>=1.29.0
```
- **boto3** - AWS SDK for Python
- **botocore** - Low-level AWS SDK

#### `order_entry_handler/app.py`
- **Purpose**: Accept and validate new orders
- **Flow**:
  1. Receives order from API Gateway
  2. Validates product IDs in DynamoDB
  3. Sends order to SQS queue
  4. Returns order confirmation

---

## 🎯 **Step 11: The Complete Request Flow**

### Example: User Creates an Order

```
┌─────────────────────────────────────────────────────────────────┐
│ Step 1: User sends POST /orders with JWT token                  │
└─────────────────────────────────────────────────────────────────┘
                             ↓
┌─────────────────────────────────────────────────────────────────┐
│ Step 2: API Gateway validates JWT with Cognito                  │
│         - If invalid → 401 Unauthorized                          │
│         - If valid → Continue                                    │
└─────────────────────────────────────────────────────────────────┘
                             ↓
┌─────────────────────────────────────────────────────────────────┐
│ Step 3: OrderEntryHandler Lambda invoked                        │
│         - Extracts user ID from JWT                              │
│         - Validates order items                                  │
└─────────────────────────────────────────────────────────────────┘
                             ↓
┌─────────────────────────────────────────────────────────────────┐
│ Step 4: Lambda queries ProductsTable (DynamoDB)                 │
│         - Check if products exist                                │
│         - Verify stock availability                              │
│         - Calculate total price                                  │
└─────────────────────────────────────────────────────────────────┘
                             ↓
┌─────────────────────────────────────────────────────────────────┐
│ Step 5: Lambda sends message to SQS Queue                       │
│         Message contains:                                        │
│         - Order ID                                               │
│         - User ID                                                │
│         - Order items                                            │
│         - Total amount                                           │
└─────────────────────────────────────────────────────────────────┘
                             ↓
┌─────────────────────────────────────────────────────────────────┐
│ Step 6: Lambda returns response to user                         │
│         { "orderId": "...", "status": "queued" }                 │
└─────────────────────────────────────────────────────────────────┘
                             ↓
┌─────────────────────────────────────────────────────────────────┐
│ Step 7: Step Functions picks message from SQS                   │
└─────────────────────────────────────────────────────────────────┘
                             ↓
┌─────────────────────────────────────────────────────────────────┐
│ Step 8: State Machine processes order                           │
│         1. Validate order                                        │
│         2. Process payment (placeholder)                         │
│         3. Update OrdersTable with status                        │
│         4. Publish to SNS topic                                  │
└─────────────────────────────────────────────────────────────────┘
                             ↓
┌─────────────────────────────────────────────────────────────────┐
│ Step 9: SNS sends notifications                                 │
│         - Email to customer                                      │
│         - Webhook to other systems                               │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🧪 **Step 12: Testing Your Code**

### Unit Testing (Local)

Create a test event file `events/auth-register.json`:
```json
{
  "body": "{\"action\":\"register\",\"email\":\"test@example.com\",\"password\":\"Test123!\",\"name\":\"Test User\"}"
}
```

Run locally:
```bash
sam local invoke AuthHandler -e events/auth-register.json
```

### Integration Testing (After Deployment)

Use the `tests/test_dev2.py` file to run automated tests.

---

## 🛠️ **Step 13: Common Tasks You Might Do**

### Task 1: Add Email Verification
Modify `auth_handler/app.py` to verify email before allowing login.

### Task 2: Add Password Reset
Create new function `handle_forgot_password()` and `handle_confirm_password()`.

### Task 3: Add Input Validation
Use **Pydantic** to validate request bodies:
```python
from pydantic import BaseModel, EmailStr

class RegisterRequest(BaseModel):
    action: str
    email: EmailStr
    password: str
    name: str
```

### Task 4: Add API Rate Limiting
Use API Gateway usage plans and API keys.

---

## 📋 **Step 14: Important Concepts to Understand**

### 1. **Serverless vs Traditional**
- **Traditional**: You manage servers, scaling, maintenance
- **Serverless**: AWS manages everything, you just write code

### 2. **Event-Driven Architecture**
- Components communicate via events (SQS, SNS)
- Decoupled: Services don't directly call each other
- Scalable: Each component scales independently

### 3. **Infrastructure as Code (IaC)**
- `template.yaml` defines all infrastructure
- Version controlled
- Reproducible across environments

### 4. **Least Privilege Permissions**
Each Lambda has **only** the permissions it needs:
```yaml
Policies:
  - Effect: Allow
    Action:
      - cognito-idp:AdminInitiateAuth  # Only what's needed
    Resource: !GetAtt UserPool.Arn
```

---

## 🎓 **Step 15: Next Steps for Learning**

### Beginner Level:
1. ✅ Read through all Lambda function code
2. ✅ Understand the template.yaml structure
3. ✅ Deploy locally with `sam local start-api`
4. ✅ Test each endpoint with curl or Postman

### Intermediate Level:
1. ✅ Deploy to AWS with `sam deploy`
2. ✅ Add new features to existing Lambdas
3. ✅ Create new Lambda functions
4. ✅ Modify DynamoDB schema

### Advanced Level:
1. ✅ Add CI/CD pipeline (GitHub Actions)
2. ✅ Implement CloudWatch dashboards
3. ✅ Add AWS X-Ray tracing
4. ✅ Implement multi-region deployment

---

## 📚 **Step 16: Key Files to Read**

Start with these files in order:

1. **README.md** - Project overview
2. **ARCHITECTURE.md** - System design diagrams
3. **template.yaml** - Infrastructure definition
4. **dev2-api-auth/lambdas/auth_handler/app.py** ⭐ (YOU ARE HERE)
5. **dev2-api-auth/lambdas/order_entry_handler/app.py**
6. **dev3-data-media/lambdas/get_products_handler/app.py**
7. **dev1-backend-core/state-machines/order-workflow.asl.json**
8. **docs/api-spec.md** - Complete API documentation
9. **docs/deployment-guide.md** - How to deploy

---

## 🆘 **Step 17: Troubleshooting**

### Issue: Lambda timeout
**Solution**: Increase `Timeout` in template.yaml

### Issue: Permissions error
**Solution**: Check IAM policies in template.yaml

### Issue: Cognito password error
**Solution**: Password must match policy (8+ chars, upper, lower, number, symbol)

### Issue: Can't access API
**Solution**: Check CORS configuration in API Gateway

---

## 🎯 **Summary: What You Need to Know**

### Your Role (Developer 2):
1. ✅ You manage **user authentication**
2. ✅ You create **API endpoints** for auth and orders
3. ✅ You work with **Cognito** and **SQS**

### Your Code:
1. ✅ `auth_handler/app.py` - Handles register/login/refresh
2. ✅ `order_entry_handler/app.py` - Accepts new orders

### Your Infrastructure:
1. ✅ Cognito User Pool
2. ✅ API Gateway
3. ✅ 2 Lambda Functions

### Dependencies:
- **Uses**: Cognito (your own), ProductsTable (Dev 1's), SQS Queue (Dev 1's)
- **Used by**: Frontend apps, other Lambda functions

---

## 🚀 **Quick Command Reference**

```bash
# Navigate to project
cd /home/esraaabdelrazek/.gemini/antigravity/scratch/ecommerce-serverless-sam

# Validate template
sam validate

# Build project
sam build

# Test locally
sam local start-api

# Deploy to AWS
sam deploy --guided

# View logs
sam logs -n AuthHandler --stack-name ecommerce-serverless-dev --tail

# Delete deployment
sam delete --stack-name ecommerce-serverless-dev
```

---

## 🎉 **You're Ready!**

You now understand:
- ✅ What this project does
- ✅ How serverless architecture works
- ✅ Your specific responsibilities
- ✅ How to read and modify the code
- ✅ How to test and deploy

**Next Action**: Try deploying locally with `sam local start-api` and test the `/auth` endpoint!

---

**Questions?** Check the `docs/` folder for more detailed guides!
