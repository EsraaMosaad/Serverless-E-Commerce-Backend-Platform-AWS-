import boto3
import sys

# Initialize DynamoDB resource
# Note: Ensure your AWS credentials are configured
dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
table = dynamodb.Table('dev-ProductsTable')

def seed_products():
    print("🚀 Seeding products into dev-ProductsTable...")
    
    products = [
        {
            'productId': 'p1',
            'name': 'High-End Laptop',
            'price': 1200,
            'description': 'Powerful laptop for developers and creators.',
            'stock': 10
        },
        {
            'productId': 'p2',
            'name': 'Wireless Mouse',
            'price': 25,
            'description': 'Ergonomic wireless mouse with long battery life.',
            'stock': 50
        },
        {
            'productId': 'p3',
            'name': 'Mechanical Keyboard',
            'price': 75,
            'description': 'RGB backlit mechanical keyboard with blue switches.',
            'stock': 20
        }
    ]
    
    try:
        for product in products:
            print(f"Adding {product['name']}...")
            table.put_item(Item=product)
        print("✅ Successfully added 3 products!")
    except Exception as e:
        print(f"❌ Error seeding products: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    seed_products()