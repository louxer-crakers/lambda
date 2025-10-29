import boto3
import json
import os
import decimal

# Helper class to convert DynamoDB's Decimal to JSON-friendly int/float
class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, decimal.Decimal):
            return int(obj) if obj % 1 == 0 else float(obj)
        return super(DecimalEncoder, self).default(obj)

# Initialize DynamoDB client
dynamodb = boto3.resource('dynamodb')
TABLE_NAME = os.environ['TABLE_NAME']
table = dynamodb.Table(TABLE_NAME)

def lambda_handler(event, context):
    try:
        # Get the 'id' from the URL path.
        # Assumes API Gateway path is something like /items/{id}
        item_id = event['pathParameters']['id']
        
        # Fetch the item from DynamoDB using its primary key.
        response = table.get_item(
            Key={'id': item_id}
        )
        
        # The 'get_item' response will contain an 'Item' key if it was found.
        if 'Item' in response:
            # If found, return 200 OK with the item data.
            # Use cls=DecimalEncoder to serialize the response.
            return {
                'statusCode': 200,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
                    'Access-Control-Allow-Methods': 'DELETE,GET,PUT,OPTIONS'
                },
                'body': json.dumps(response['Item'], cls=DecimalEncoder)
            }
        else:
            # If 'Item' key is not in the response, it means 404 Not Found.
            return {
                'statusCode': 404,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
                    'Access-Control-Allow-Methods': 'DELETE,GET,PUT,OPTIONS'
                },
                'body': json.dumps({'message': 'Item not found'})
            }
            
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
                'Access-Control-Allow-Methods': 'DELETE,GET,PUT,OPTIONS'
            },
            'body': json.dumps({'message': f'Internal server error: {str(e)}'})
        }