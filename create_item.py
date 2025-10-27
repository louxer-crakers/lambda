import boto3
import json
import os
import decimal

# --- English Explanation ---
# DynamoDB stores numbers as 'Decimal' objects, which JSON doesn't understand.
# This Helper class converts Python's Decimal type to a normal integer or float
# when we are serializing (dumping) data back to JSON.
class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, decimal.Decimal):
            return int(obj) if obj % 1 == 0 else float(obj)
        return super(DecimalEncoder, self).default(obj)

# Initialize the DynamoDB client
dynamodb = boto3.resource('dynamodb')
# Get the table name from the Lambda's environment variables
TABLE_NAME = os.environ['TABLE_NAME']
table = dynamodb.Table(TABLE_NAME)

def lambda_handler(event, context):
    try:
        # --- English Explanation ---
        # 1. Load the request body (which is a JSON string) into a Python dictionary.
        # 2. 'parse_float=decimal.Decimal' is crucial. It tells json.loads()
        #    to convert any numbers (like 10.50) into a Decimal object,
        #    which is what DynamoDB's put_item expects.
        body = json.loads(event.get('body', '{}'), parse_float=decimal.Decimal)

        # Basic validation: ensure the primary key 'id' is present.
        if 'id' not in body:
            return {
                'statusCode': 400,
                'body': json.dumps({'message': 'Error: "id" (primary key) is required in the body'})
            }

        item = body
        
        # --- English Explanation ---
        # The put_item operation creates a new item or *replaces* an old item
        # entirely if the 'id' already exists.
        table.put_item(Item=item)
        
        # Return a 201 Created status
        return {
            'statusCode': 201, 
            'headers': {'Content-Type': 'application/json'},
            # Use cls=DecimalEncoder to convert any Decimals in the 'item' back to numbers for the JSON response
            'body': json.dumps({'message': 'Item created successfully', 'item': item}, cls=DecimalEncoder)
        }
        
    except Exception as e:
        # Generic error handler
        return {
            'statusCode': 500,
            'body': json.dumps({'message': f'Internal server error: {str(e)}'})
        }