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
        # Get the 'id' from the URL path
        item_id = event['pathParameters']['id']
        
        # Load the request body, converting numbers to Decimal
        body = json.loads(event.get('body', '{}'), parse_float=decimal.Decimal)
        
        # This is a simple example that *only* updates 'name' and 'price'.
        # A more complex function would dynamically build the UpdateExpression
        # based on the keys present in the 'body'.
        if 'name' not in body or 'price' not in body:
             return {'statusCode': 400, 'body': json.dumps({'message': 'Error: "name" and "price" are required in the body for update'})}

        # 'UpdateItem' is the most complex operation.
        # - Key: Specifies *which* item to update.
        # - UpdateExpression: Tells DynamoDB *what* to do. "set #n = :n" means
        #   "set the attribute 'name' to the value ':n'".
        # - ExpressionAttributeNames (#): A placeholder for attribute names.
        #   This is needed if your attribute name is a reserved_word (like 'name').
        # - ExpressionAttributeValues (:): A placeholder for attribute values.
        #   This provides the actual data.
        # - ReturnValues: Asks DynamoDB to return the *new* values of the attributes that were just updated.
        response = table.update_item(
            Key={'id': item_id},
            UpdateExpression="set #n = :n, #p = :p",
            ExpressionAttributeNames={
                '#n': 'name',
                '#p': 'price'
            },
            ExpressionAttributeValues={
                ':n': body['name'],
                ':p': body['price']
            },
            ReturnValues="UPDATED_NEW" 
        )
        
        return {
            'statusCode': 200,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({'message': 'Item updated successfully', 'updatedAttributes': response['Attributes']}, cls=DecimalEncoder)
        }
        
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'message': f'Internal server error: {str(e)}'})
        }