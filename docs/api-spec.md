# API Specification

## Base URL
```
https://{api-id}.execute-api.{region}.amazonaws.com/{environment}/
```

## Authentication

Most endpoints require authentication via AWS Cognito. Include the JWT token in the Authorization header:

```
Authorization: Bearer <JWT_TOKEN>
```

## Endpoints

### 1. Authentication

#### POST /auth
User authentication operations (register, login, refresh token)

**Authentication**: Not required

**Request Body**:
```json
{
  "action": "register" | "login" | "refresh",
  "email": "user@example.com",
  "password": "SecurePass123!",
  "name": "User Name"  // Required for registration only
}
```

**Register Response** (201):
```json
{
  "message": "User registered successfully",
  "userId": "user-uuid",
  "email": "user@example.com"
}
```

**Login Response** (200):
```json
{
  "message": "Login successful",
  "accessToken": "eyJraWQiOiI...",
  "idToken": "eyJraWQiOiI...",
  "refreshToken": "eyJjdHkiOiI...",
  "expiresIn": 3600
}
```

**Error Responses**:
- `400`: Missing required fields or invalid password format
- `401`: Invalid credentials
- `409`: User already exists

---

### 2. Products

#### GET /products
Retrieve product list

**Authentication**: Not required (public endpoint)

**Query Parameters**:
- `category` (optional): Filter by category
- `limit` (optional, default: 50, max: 100): Number of items to return
- `lastKey` (optional): Pagination token from previous response

**Example Request**:
```
GET /products?category=electronics&limit=20
```

**Response** (200):
```json
{
  "products": [
    {
      "productId": "prod-123",
      "name": "Product Name",
      "description": "Product description",
      "price": 29.99,
      "category": "electronics",
      "imageUrl": "https://...",
      "inStock": true,
      "createdAt": "2024-01-01T00:00:00Z"
    }
  ],
  "count": 20,
  "scannedCount": 20,
  "hasMore": true,
  "lastKey": "{\"productId\":\"prod-123\"}"
}
```

**Error Responses**:
- `400`: Invalid parameters
- `500`: Database error

---

#### GET /products/upload
Generate S3 pre-signed URL for product image upload

**Authentication**: Required

**Query Parameters**:
- `filename` (optional): Original filename
- `contentType` (optional, default: `image/jpeg`): MIME type
  - Allowed: `image/jpeg`, `image/jpg`, `image/png`, `image/gif`, `image/webp`
- `expiresIn` (optional, default: 300, max: 3600): URL validity in seconds

**Example Request**:
```
GET /products/upload?filename=product.jpg&contentType=image/jpeg&expiresIn=600
```

**Response** (200):
```json
{
  "uploadUrl": "https://bucket.s3.amazonaws.com/products/20240101/uuid.jpg?X-Amz-Signature=...",
  "fileUrl": "https://bucket.s3.amazonaws.com/products/20240101/uuid.jpg",
  "key": "products/20240101/uuid.jpg",
  "expiresIn": 600,
  "expiresAt": 1704067200,
  "instructions": {
    "method": "PUT",
    "headers": {
      "Content-Type": "image/jpeg"
    },
    "note": "Upload the file directly to the uploadUrl using PUT method"
  }
}
```

**Upload Example**:
```bash
curl -X PUT "https://bucket.s3.amazonaws.com/products/..." \
  -H "Content-Type: image/jpeg" \
  --data-binary @product.jpg
```

**Error Responses**:
- `400`: Invalid content type
- `401`: Unauthorized
- `500`: Failed to generate URL

---

### 3. Orders

#### POST /orders
Create a new order

**Authentication**: Required

**Request Body**:
```json
{
  "items": [
    {
      "productId": "prod-123",
      "quantity": 2
    },
    {
      "productId": "prod-456",
      "quantity": 1
    }
  ],
  "shippingAddress": {
    "street": "123 Main Street",
    "city": "Boston",
    "state": "MA",
    "zip": "02101",
    "country": "USA"
  }
}
```

**Response** (201):
```json
{
  "message": "Order created successfully",
  "orderId": "order-uuid",
  "status": "PENDING",
  "totalAmount": 89.97,
  "sqsMessageId": "message-id"
}
```

**Error Responses**:
- `400`: Invalid request (missing items, invalid quantities, etc.)
- `401`: Unauthorized
- `404`: Product not found
- `500`: Internal server error

---

## Common Response Headers

All responses include:
```
Content-Type: application/json
Access-Control-Allow-Origin: *
Access-Control-Allow-Headers: Content-Type,Authorization
Access-Control-Allow-Methods: GET,POST,PUT,DELETE,OPTIONS
```

## Error Response Format

```json
{
  "error": "Error type",
  "message": "Detailed error message"
}
```

## Rate Limiting

API Gateway has default throttling:
- **Burst**: 5,000 requests per second
- **Rate**: 10,000 requests per second per account

For production, implement custom throttling per endpoint.

## Authentication Flow

1. **Register**: POST /auth with `action=register`
2. **Login**: POST /auth with `action=login` to get tokens
3. **Authorized Request**: Include `accessToken` in Authorization header
4. **Token Refresh**: When `accessToken` expires, POST /auth with `action=refresh` and `refreshToken`

## Data Models

### Product
```typescript
{
  productId: string;        // Partition key
  name: string;
  description: string;
  price: number;
  category: string;
  imageUrl?: string;
  inStock: boolean;
  stock?: number;
  createdAt: string;       // ISO 8601
  updatedAt: string;       // ISO 8601
}
```

### Order
```typescript
{
  orderId: string;         // Partition key
  userId: string;          // From Cognito
  items: Array<{
    productId: string;
    quantity: number;
  }>;
  shippingAddress: {
    street: string;
    city: string;
    state: string;
    zip: string;
    country: string;
  };
  totalAmount: number;
  status: 'PENDING' | 'PROCESSING' | 'COMPLETED' | 'FAILED';
  createdAt: string;       // ISO 8601
  updatedAt: string;       // ISO 8601
}
```

## Testing with cURL

### Register a User
```bash
curl -X POST https://api-url/dev/auth \
  -H "Content-Type: application/json" \
  -d '{
    "action": "register",
    "email": "test@example.com",
    "password": "Test123!",
    "name": "Test User"
  }'
```

### Login
```bash
curl -X POST https://api-url/dev/auth \
  -H "Content-Type: application/json" \
  -d '{
    "action": "login",
    "email": "test@example.com",
    "password": "Test123!"
  }'
```

### Get Products
```bash
curl -X GET https://api-url/dev/products
```

### Create Order
```bash
TOKEN="your-access-token"

curl -X POST https://api-url/dev/orders \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer ${TOKEN}" \
  -d '{
    "items": [
      {"productId": "prod-123", "quantity": 2}
    ],
    "shippingAddress": {
      "street": "123 Main St",
      "city": "Boston",
      "state": "MA",
      "zip": "02101",
      "country": "USA"
    }
  }'
```

### Get Upload URL
```bash
TOKEN="your-access-token"

curl -X GET "https://api-url/dev/products/upload?filename=product.jpg" \
  -H "Authorization: Bearer ${TOKEN}"
```

## Postman Collection

Import the following environment variables in Postman:
- `base_url`: Your API Gateway URL
- `access_token`: JWT token from login
- `refresh_token`: Refresh token from login

## WebSocket Support (Future)

For real-time order updates, WebSocket API can be added in future iterations.
