#!/bin/bash

# E-Commerce Serverless SAM - Validation & Quick Start Script
# Run this script to validate the project setup

set -e

echo "=========================================="
echo "E-Commerce Serverless SAM - Validation"
echo "=========================================="
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check prerequisites
echo "📋 Checking Prerequisites..."

# Check AWS CLI
if command -v aws &> /dev/null; then
    echo -e "${GREEN}✓${NC} AWS CLI installed: $(aws --version)"
else
    echo -e "${RED}✗${NC} AWS CLI not found. Install from: https://aws.amazon.com/cli/"
    exit 1
fi

# Check SAM CLI
if command -v sam &> /dev/null; then
    echo -e "${GREEN}✓${NC} SAM CLI installed: $(sam --version)"
else
    echo -e "${RED}✗${NC} SAM CLI not found. Install: pip install aws-sam-cli"
    exit 1
fi

# Check Python 3.9
if command -v python3.9 &> /dev/null; then
    echo -e "${GREEN}✓${NC} Python 3.9 installed"
elif command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
    echo -e "${YELLOW}⚠${NC} Python 3.9 recommended, found: $PYTHON_VERSION"
else
    echo -e "${RED}✗${NC} Python 3 not found"
    exit 1
fi

echo ""

# Validate SAM template
echo "🔍 Validating SAM Template..."
if sam validate --lint; then
    echo -e "${GREEN}✓${NC} template.yaml is valid"
else
    echo -e "${RED}✗${NC} template.yaml validation failed"
    exit 1
fi

echo ""

# Check file structure
echo "📁 Validating Project Structure..."

REQUIRED_FILES=(
    "template.yaml"
    "samconfig.toml"
    "README.md"
    "dev1-backend-core/state-machines/order-workflow.asl.json"
    "dev2-api-auth/lambdas/auth_handler/app.py"
    "dev2-api-auth/lambdas/order_entry_handler/app.py"
    "dev3-data-media/lambdas/get_products_handler/app.py"
    "dev3-data-media/lambdas/upload_url_handler/app.py"
)

for file in "${REQUIRED_FILES[@]}"; do
    if [ -f "$file" ]; then
        echo -e "${GREEN}✓${NC} $file"
    else
        echo -e "${RED}✗${NC} Missing: $file"
        exit 1
    fi
done

echo ""

# Count Lambda functions
echo "🔧 Lambda Functions Summary:"
LAMBDA_COUNT=$(grep -c "Type: AWS::Serverless::Function" template.yaml || true)
echo "   Total Lambda Functions: $LAMBDA_COUNT"

# Count DynamoDB tables
DYNAMODB_COUNT=$(grep -c "Type: AWS::DynamoDB::Table" template.yaml || true)
echo "   DynamoDB Tables: $DYNAMODB_COUNT"

# Count SQS queues
SQS_COUNT=$(grep -c "Type: AWS::SQS::Queue" template.yaml || true)
echo "   SQS Queues: $SQS_COUNT"

# Count SNS topics
SNS_COUNT=$(grep -c "Type: AWS::SNS::Topic" template.yaml || true)
echo "   SNS Topics: $SNS_COUNT"

echo ""

# Check AWS credentials
echo "🔑 Checking AWS Credentials..."
if aws sts get-caller-identity &> /dev/null; then
    AWS_ACCOUNT=$(aws sts get-caller-identity --query Account --output text)
    AWS_REGION=$(aws configure get region || echo "not-set")
    echo -e "${GREEN}✓${NC} AWS Account: $AWS_ACCOUNT"
    echo -e "${GREEN}✓${NC} Default Region: $AWS_REGION"
else
    echo -e "${YELLOW}⚠${NC} AWS credentials not configured. Run: aws configure"
fi

echo ""
echo "=========================================="
echo -e "${GREEN}✓ Validation Complete!${NC}"
echo "=========================================="
echo ""
echo "📚 Next Steps:"
echo "   1. Read docs/developer-guide.md for team organization"
echo "   2. Review docs/api-spec.md for API documentation"
echo "   3. Build: sam build"
echo "   4. Deploy: sam deploy --guided"
echo "   5. Test locally: sam local start-api"
echo ""
echo "🚀 Happy Hacking!"
