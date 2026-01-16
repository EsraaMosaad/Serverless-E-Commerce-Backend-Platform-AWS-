# 🚀 E-Commerce Serverless Backend - AWS SAM

A high-performance, scalable e-commerce backend built using **AWS SAM**, **Python 3.9**, and **Step Functions**. This project was designed for a team of 3 developers to work in parallel on different architectural components.

---

## 🔗 Live API & Testing
- **API Gateway URL:** `https://kfmg30d5hg.execute-api.us-east-1.amazonaws.com/dev/`
- **Postman Collection:** [ecommerce_api.postman_collection.json](./ecommerce_api.postman_collection.json)
- **Environment:** `dev` (Single environment setup)

---

## 🛠️ Team Organization & Scope

### 🧑‍💻 Developer 1: Backend Core & Orchestration
- **Infrastructure:** DynamoDB (Products, Orders), SQS (Order Queue), SNS (Notifications).
- **Orchestration:** Step Functions (Order Processing Workflow).
- **Lambdas:** `ValidateOrderFunction`, `ProcessPaymentFunction`.
- **Directory:** `dev1-backend-core/`

### 🧑‍💻 Developer 2: API & Authentication
- **Security:** Cognito User Pool (Auto-confirm enabled).
- **API:** API Gateway with Cognito Authorizer.
- **Lambdas:** `AuthHandler`, `OrderEntryHandler`.
- **Directory:** `dev2-api-auth/`

### 🧑‍💻 Developer 3: Data & Media Management
- **Media:** S3 Bucket for Product Images (Pre-signed URL uploads).
- **Lambdas:** `GetProductsHandler`, `UploadUrlHandler`.
- **Directory:** `dev3-data-media/`

---

## 📂 Project Structure

```text
ecommerce-serverless-sam/
├── template.yaml                 # Master SAM template
├── samconfig.toml               # SAM CLI configuration
├── README.md                    # This file (Main Entry Point)
├── seed_products.py             # Data seeding script for DynamoDB
├── validate.sh                  # Environment validation script
├── ecommerce_api.postman_collection.json # API Testing Collection
│
├── dev1-backend-core/           # Developer 1: Workflow & Core Logic
│   ├── lambdas/                 # Validation & Payment handlers
│   └── state-machines/          # Order Workflow (Step Functions)
│
├── dev2-api-auth/               # Developer 2: API & Security
│   └── lambdas/                 # Auth & Order Entry handlers
│
├── dev3-data-media/             # Developer 3: Products & S3
│   └── lambdas/                 # Product listing & Upload handlers
│
└── docs/                        # Detailed Documentation
    ├── architecture.md          # System design & diagrams
    ├── step-by-step-guide.md    # Comprehensive project walkthrough
    ├── project-summary.md       # High-level overview
    ├── api-spec.md              # API documentation
    └── deployment-guide.md      # How to deploy to AWS
```

---

## ⚡ Quick Start

### 1. Prerequisites
- AWS CLI configured with credentials.
- AWS SAM CLI installed.
- Python 3.9.

### 2. Build and Deploy
```bash
# Build the application
sam build

# Deploy to AWS
sam deploy --stack-name ecommerce-serverless-dev-v2 --region us-east-1 --s3-bucket ecommerce-sam-artifacts-1768394275 --capabilities CAPABILITY_IAM --no-confirm-changeset
```

### 3. Seed Data
```bash
python3 seed_products.py
```

---

## 📖 Documentation Links
- [Architecture & Flow](./docs/architecture.md)
- [Step-by-Step Guide](./docs/step-by-step-guide.md)
- [API Specification](./docs/api-spec.md)
- [Project Summary](./docs/project-summary.md)

---

## 🚀 API Endpoints Summary
- `POST /auth` - Register/Login/Refresh (Public)
- `GET /products` - List all products (Public)
- `POST /orders` - Create new order (Authenticated)
- `GET /products/upload` - Get S3 upload URL (Authenticated)
