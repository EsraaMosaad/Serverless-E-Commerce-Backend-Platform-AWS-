# 🚀 Quick Reference

## 🔗 API Endpoint
**Base URL**: `https://kfmg30d5hg.execute-api.us-east-1.amazonaws.com/dev/`

## 🧪 Common Commands

### Register User
```bash
curl -X POST https://kfmg30d5hg.execute-api.us-east-1.amazonaws.com/dev/auth \
  -H "Content-Type: application/json" \
  -d '{
    "action": "register",
    "email": "test@example.com",
    "password": "Test123!",
    "name": "Test User"
  }'
```

### Login User
```bash
curl -X POST https://kfmg30d5hg.execute-api.us-east-1.amazonaws.com/dev/auth \
  -H "Content-Type: application/json" \
  -d '{
    "action": "login",
    "email": "test@example.com",
    "password": "Test123!"
  }'
```

### Create Order (Requires Token)
```bash
curl -X POST https://kfmg30d5hg.execute-api.us-east-1.amazonaws.com/dev/orders \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <YOUR_ACCESS_TOKEN>" \
  -d '{
    "items": [
      {"productId": "prod-1", "quantity": 1}
    ]
  }'
```

## 🛠️ SAM Commands

### Deploy Updates
```bash
sam deploy \
  --stack-name ecommerce-serverless-dev-v2 \
  --region us-east-1 \
  --s3-bucket ecommerce-sam-artifacts-1768394275 \
  --capabilities CAPABILITY_IAM \
  --no-confirm-changeset
```

### View Logs
```bash
sam logs -n AuthHandler --stack-name ecommerce-serverless-dev-v2 --tail
```
