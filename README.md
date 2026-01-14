# E-Commerce Serverless Backend - AWS SAM

## Architecture Overview
Serverless e-commerce backend built with AWS SAM for a 2-day hackathon by a team of 3 developers.

## Developer Assignments

### Developer 1: Backend Core & Orchestration
**Scope:**
- DynamoDB Tables (Products, Orders)
- SQS Queue (Order Processing)
- SNS Topic (Order Completed)
- Step Functions State Machine (Order Workflow)

**Directory:** `dev1-backend-core/`

### Developer 2: API & Authentication
**Scope:**
- Cognito User Pool
- API Gateway with Cognito Authorizer
- Auth Handler Lambda
- Order Entry Handler Lambda

**Directory:** `dev2-api-auth/`

### Developer 3: Data & Media Management
**Scope:**
- S3 Bucket (Product Images)
- Get Products Handler Lambda
- Upload URL Handler Lambda

**Directory:** `dev3-data-media/`

## Project Structure

```
ecommerce-serverless-sam/
├── template.yaml                 # Master SAM template
├── samconfig.toml               # SAM CLI configuration
├── README.md                    # This file
│
├── dev1-backend-core/           # Developer 1 workspace
│   ├── lambdas/
│   │   └── (No direct Lambdas, manages infrastructure)
│   └── state-machines/
│       └── order-workflow.asl.json
│
├── dev2-api-auth/               # Developer 2 workspace
│   └── lambdas/
│       ├── auth_handler/
│       │   ├── app.py
│       │   └── requirements.txt
│       └── order_entry_handler/
│           ├── app.py
│           └── requirements.txt
│
├── dev3-data-media/             # Developer 3 workspace
│   └── lambdas/
│       ├── get_products_handler/
│       │   ├── app.py
│       │   └── requirements.txt
│       └── upload_url_handler/
│           ├── app.py
│           └── requirements.txt
│
├── shared/                      # Shared utilities
│   └── layers/
│       └── common/
│           └── python/
│               └── utils.py
│
├── tests/                       # Integration tests
│   ├── test_dev1.py
│   ├── test_dev2.py
│   └── test_dev3.py
│
└── docs/                        # Documentation
    ├── api-spec.md
    └── deployment-guide.md
```

## Quick Start

### Prerequisites
- AWS CLI configured
- AWS SAM CLI installed
- Python 3.9

### Build and Deploy
```bash
# Build the application
sam build

# Deploy (guided)
sam deploy --guided

# Deploy (after first guided deployment)
sam deploy
```

### Local Testing
```bash
# Start API locally
sam local start-api

# Invoke a specific function
sam local invoke GetProductsHandler
```

## Development Workflow

1. Each developer works in their respective directory
2. Update `template.yaml` only when adding new resources
3. Commit changes frequently to avoid merge conflicts
4. Test locally before deploying

## API Endpoints

- `POST /auth` - Authentication (AuthHandler)
- `POST /orders` - Create new order (OrderEntryHandler)
- `GET /products` - List all products (GetProductsHandler)
- `GET /products/upload` - Get S3 presigned URL (UploadUrlHandler)
