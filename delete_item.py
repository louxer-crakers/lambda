import boto3
import json
import os

# Initialize DynamoDB client
dynamodb = boto3.resource('dynamodb')
TABLE_NAME = os.environ['TABLE_NAME']
table = dynamodb.Table(TABLE_NAME)

def lambda_handler(event, context):
    try:
        # Get the 'id' from the URL path
        item_id = event['pathParameters']['id']
        
        # Deletes the item corresponding to the primary key.
        # This operation is idempotent: running it multiple times on the
        # same 'id' will not cause an error (it just does nothing
        # if the item is already gone).
        table.delete_item(
            Key={'id': item_id}
            # You can add a 'ConditionExpression' here to
            # prevent deletion if certain conditions aren't met.
        )
        
        # Return a 200 OK (or 204 No Content is also common)
        return {
            'statusCode': 200,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({'message': 'Item deleted successfully'})
        }
        
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'message': f'Internal server error: {str(e)}'})
        }