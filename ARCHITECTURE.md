# E-Commerce Serverless Architecture Diagram

## System Architecture Flow

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           CLIENT APPLICATIONS                                │
│                      (Web Browser, Mobile App, etc.)                         │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                          AWS API GATEWAY (REST)                              │
│                         + Cognito Authorizer                                 │
├─────────────────────────────────────────────────────────────────────────────┤
│  Endpoints:                                                                  │
│  • POST   /auth              → AuthHandler (no auth)                         │
│  • GET    /products          → GetProductsHandler (no auth)                  │
│  • GET    /products/upload   → UploadUrlHandler (auth required)              │
│  • POST   /orders            → OrderEntryHandler (auth required)             │
└─────────────────────────────────────────────────────────────────────────────┘
         │              │                    │                    │
         │              │                    │                    │
         ▼              ▼                    ▼                    ▼
┌──────────────┐ ┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│ AuthHandler  │ │GetProducts   │  │UploadUrl     │  │OrderEntry    │
│   Lambda     │ │  Handler     │  │  Handler     │  │  Handler     │
│              │ │   Lambda     │  │   Lambda     │  │   Lambda     │
│ (Developer 2)│ │(Developer 3) │  │(Developer 3) │  │(Developer 2) │
└──────────────┘ └──────────────┘  └──────────────┘  └──────────────┘
         │              │                    │                    │
         ▼              ▼                    ▼                    ▼
┌──────────────┐ ┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│  Cognito     │ │  DynamoDB    │  │      S3      │  │     SQS      │
│  User Pool   │ │  Products    │  │   Product    │  │    Order     │
│              │ │    Table     │  │   Images     │  │ Processing   │
│ (Developer 2)│ │(Developer 1) │  │(Developer 3) │  │   Queue      │
└──────────────┘ └──────────────┘  └──────────────┘  └──────────────┘
                                                                │
                                                                ▼
                                                    ┌──────────────────┐
                                                    │ Step Functions   │
                                                    │    Order         │
                                                    │   Processing     │
                                                    │   Workflow       │
                                                    │ (Developer 1)    │
                                                    └──────────────────┘
                                                                │
                                                                ▼
                                                    ┌──────────────────┐
                                                    │   DynamoDB       │
                                                    │    Orders        │
                                                    │     Table        │
                                                    │ (Developer 1)    │
                                                    └──────────────────┘
                                                                │
                                                                ▼
                                                    ┌──────────────────┐
                                                    │   SNS Topic      │
                                                    │     Order        │
                                                    │   Completed      │
                                                    │ (Developer 1)    │
                                                    └──────────────────┘
```

## Component Interaction Matrix

| Component | Interacts With | Purpose |
|-----------|----------------|---------|
| **API Gateway** | All Lambdas | Routes HTTP requests |
| **Cognito** | API Gateway, AuthHandler | User authentication |
| **AuthHandler** | Cognito User Pool | Register/login users |
| **GetProductsHandler** | ProductsTable | Retrieve products |
| **UploadUrlHandler** | S3 Bucket | Generate upload URLs |
| **OrderEntryHandler** | ProductsTable, SQS | Validate and queue orders |
| **SQS Queue** | Step Functions | Trigger order workflow |
| **Step Functions** | OrdersTable, SNS | Orchestrate order processing |
| **ProductsTable** | GetProducts, OrderEntry | Store product catalog |
| **OrdersTable** | Step Functions | Store orders |
| **S3 Bucket** | UploadUrlHandler | Store product images |
| **SNS Topic** | Step Functions | Send notifications |

## Developer Ownership Map

```
┌─────────────────────────────────────────────────────────────────┐
│                        Developer 1                               │
│                  Backend Core & Orchestration                    │
├─────────────────────────────────────────────────────────────────┤
│ • DynamoDB ProductsTable                                         │
│ • DynamoDB OrdersTable                                           │
│ • SQS OrderProcessingQueue                                       │
│ • SQS OrderProcessingDLQ                                         │
│ • SNS OrderCompletedTopic                                        │
│ • Step Functions OrderProcessingWorkflow                         │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                        Developer 2                               │
│                      API & Authentication                        │
├─────────────────────────────────────────────────────────────────┤
│ • Cognito User Pool                                              │
│ • Cognito User Pool Client                                       │
│ • API Gateway ECommerceApi                                       │
│ • Lambda AuthHandler                                             │
│ • Lambda OrderEntryHandler                                       │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                        Developer 3                               │
│                    Data & Media Management                       │
├─────────────────────────────────────────────────────────────────┤
│ • S3 ProductImagesBucket                                         │
│ • Lambda GetProductsHandler                                      │
│ • Lambda UploadUrlHandler                                        │
└─────────────────────────────────────────────────────────────────┘
```

## Data Flow: Order Creation

```
1. User
    │
    │ POST /orders (with JWT)
    ▼
2. API Gateway
    │
    │ Validate JWT with Cognito
    ▼
3. OrderEntryHandler Lambda
    │
    ├─→ Validate items against ProductsTable
    ├─→ Calculate total amount
    └─→ Send message to SQS
          │
          ▼
4. SQS OrderProcessingQueue
    │
    │ Trigger (SQS Event)
    ▼
5. Step Functions Workflow
    │
    ├─→ Validate Order (Pass State)
    ├─→ Process Payment (Pass State - placeholder)
    ├─→ Update OrdersTable (DynamoDB UpdateItem)
    └─→ Publish to SNS Topic
          │
          ▼
6. SNS OrderCompletedTopic
    │
    └─→ Email/SMS subscribers (to be configured)
```

## Data Flow: Product Image Upload

```
1. User (authenticated)
    │
    │ GET /products/upload
    ▼
2. API Gateway
    │
    │ Validate JWT
    ▼
3. UploadUrlHandler Lambda
    │
    └─→ Generate pre-signed URL from S3
          │
          │ Return URL to user
          ▼
4. User uploads directly to S3
    │
    │ PUT to pre-signed URL
    ▼
5. S3 ProductImagesBucket
    │
    └─→ Image stored securely
```

## Security Layers

```
┌─────────────────────────────────────────────────────────────────┐
│ Layer 1: HTTPS Only (API Gateway enforced)                      │
└─────────────────────────────────────────────────────────────────┘
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│ Layer 2: Cognito JWT Authentication                             │
└─────────────────────────────────────────────────────────────────┘
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│ Layer 3: IAM Least-Privilege Policies                           │
└─────────────────────────────────────────────────────────────────┘
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│ Layer 4: Private S3 Bucket (pre-signed URLs only)               │
└─────────────────────────────────────────────────────────────────┘
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│ Layer 5: VPC (optional, for production)                         │
└─────────────────────────────────────────────────────────────────┘
```

## Scalability Design

```
Component              Auto-Scaling Method
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
API Gateway            Automatic (AWS managed)
Lambda Functions       Automatic (concurrent executions)
DynamoDB               PAY_PER_REQUEST (on-demand)
SQS                    Unlimited throughput
SNS                    Unlimited fanout
Step Functions         Automatic (execution quota)
S3                     Infinite storage
```

## Cost Optimization

```
Resource              Billing Model         Optimization
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Lambda                Per invocation/ms     Right-sized memory
DynamoDB              PAY_PER_REQUEST       No idle capacity costs
API Gateway           Per request           Response caching
S3                    Per GB/request        Lifecycle policies
SNS                   Per message           Batching
SQS                   Per request           Long polling
CloudWatch Logs       Per GB ingested       Retention policies
```

## Monitoring & Observability

```
┌──────────────────────────────────────────────────────────────────┐
│                       CloudWatch Logs                             │
│  • All Lambda execution logs                                      │
│  • API Gateway access logs                                        │
│  • Step Functions execution logs                                  │
└──────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌──────────────────────────────────────────────────────────────────┐
│                      CloudWatch Metrics                           │
│  • Lambda duration, errors, throttles                             │
│  • DynamoDB read/write capacity                                   │
│  • SQS message count, age                                         │
│  • API Gateway 4xx/5xx errors                                     │
└──────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌──────────────────────────────────────────────────────────────────┐
│                      CloudWatch Alarms                            │
│  • SQS DLQ message count > 0                                      │
│  • Lambda error rate > 5%                                         │
│  • API Gateway 5xx rate > 1%                                      │
└──────────────────────────────────────────────────────────────────┘
```

## Deployment Pipeline (Future)

```
┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐
│   Git    │───▶│  Build   │───▶│   Test   │───▶│  Deploy  │
│  Commit  │    │  (SAM)   │    │  (Auto)  │    │  (SAM)   │
└──────────┘    └──────────┘    └──────────┘    └──────────┘
                                                      │
                                    ┌─────────────────┼─────────────────┐
                                    ▼                 ▼                 ▼
                                 ┌─────┐          ┌─────┐          ┌─────┐
                                 │ Dev │          │Stag │          │Prod │
                                 └─────┘          └─────┘          └─────┘
```

---

**Legend**:
- Rectangle: AWS Service/Resource
- Arrow: Data flow or dependency
- (Developer X): Ownership assignment
