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
        
        # --- Start: Dynamic Update Logic ---
        # We will build the UpdateExpression, Names, and Values dynamically
        
        update_expression_parts = []
        expression_attribute_names = {}
        expression_attribute_values = {}
        
        # Iterate over all key-value pairs in the request body
        for key, value in body.items():
            # --- English Explanation ---
            # We must skip the primary key ('id'). 
            # The 'id' is used in the 'Key' parameter, not in the 'UpdateExpression'.
            if key != 'id':
                # Create a placeholder for the attribute name (e.g., #nama)
                attr_name_placeholder = f"#{key}"
                # Create a placeholder for the attribute value (e.g., :nama)
                attr_val_placeholder = f":{key}"
                
                # Add to our expression parts: "#nama = :nama"
                update_expression_parts.append(f"{attr_name_placeholder} = {attr_val_placeholder}")
                # Add to our names dict: {'#nama': 'nama'}
                expression_attribute_names[attr_name_placeholder] = key
                # Add to our values dict: {':nama': 'Budi (Updated)'}
                expression_attribute_values[attr_val_placeholder] = value

        # --- English Explanation ---
        # Check if there is anything to update.
        # If the body was empty or only contained an 'id', this list will be empty.
        if not update_expression_parts:
            return {
                'statusCode': 400,
                'body': json.dumps({'message': 'Error: Request body must contain attributes to update (excluding "id")'})
            }

        # --- English Explanation ---
        # Join all parts into the final UpdateExpression string.
        # e.g., "set #nama_lengkap = :nama_lengkap, #kota = :kota"
        update_expression = "set " + ", ".join(update_expression_parts)

        # Call the dynamic UpdateItem operation
        response = table.update_item(
            Key={'id': item_id},
            UpdateExpression=update_expression,
            ExpressionAttributeNames=expression_attribute_names,
            ExpressionAttributeValues=expression_attribute_values,
            ReturnValues="UPDATED_NEW"
        )
        # --- End: Dynamic Update Logic ---
        
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