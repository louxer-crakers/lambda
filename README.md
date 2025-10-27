# Serverless CRUD API with Lambda and DynamoDB

This project demonstrates a serverless CRUD (Create, Read, Update, Delete) backend using **Amazon API Gateway**, **AWS Lambda**, and **DynamoDB**.

The architecture follows a single-purpose function model, where each CRUD operation is handled by its own dedicated Lambda function. This approach provides better separation of concerns, easier maintenance, and more granular security and scaling.

This project consists of 5 Lambda functions:
1.  **Create:** Creates a new item in the DynamoDB table.
2.  **Read:** Retrieves a single item by its `id`.
3.  **List:** Retrieves all items from the table.
4.  **Update:** Updates specific attributes of an existing item.
5.  **Delete:** Deletes an item from the table.

---

## API Gateway & Test Payloads

This is an example of how your API Gateway endpoints would be configured and how you can test them using Postman or `curl`.

**Assumptions:**
* Your API Gateway endpoint is: `https://api.example.com/items`
* The DynamoDB table's primary key is `id` (String).
* The item we are working with has an `id` of `item-123`.

---

### 1. Create (POST)

* **Endpoint:** `POST /items`
* **Action:** Creates a new item. The `id` and other attributes must be in the request body.

#### Postman Test:
1.  Set the method to **POST**.
2.  Set the URL to: `https://api.example.com/items`
3.  Go to the **Body** tab.
4.  Select **raw**.
5.  Select **JSON** from the dropdown.
6.  Paste the following into the body:
    ```json
    {
        "id": "item-123",
        "name": "Blue Widget",
        "price": 19.99,
        "inStock": true
    }
    ```
7.  Click **Send**.

#### `curl` Test:
```bash
curl -X POST '[https://api.example.com/items](https://api.example.com/items)' \
-H 'Content-Type: application/json' \
-d '{
    "id": "item-123",
    "name": "Blue Widget",
    "price": 19.99,
    "inStock": true
}'
```

#### Success Response (201 Created):
```json
{
    "message": "Item created successfully",
    "item": {
        "id": "item-123",
        "name": "Blue Widget",
        "price": 19.99,
        "inStock": true
    }
}
```

---

### 2. Read (GET - Single Item)

* **Endpoint:** `GET /items/{id}`
* **Action:** Retrieves a single item using the `id` from the URL path.

#### Postman Test:
1.  Set the method to **GET**.
2.  Set the URL to: `https://api.example.com/items/item-123`
3.  Click **Send**.

#### `curl` Test:
```bash
curl -X GET '[https://api.example.com/items/item-123](https://api.example.com/items/item-123)'
```

#### Success Response (200 OK):
```json
{
    "id": "item-123",
    "name": "Blue Widget",
    "price": 19.99,
    "inStock": true
}
```

#### Failure Response (404 Not Found):
```json
{
    "message": "Item not found"
}
```

---

### 3. Update (PUT)

* **Endpoint:** `PUT /items/{id}`
* **Action:** Updates specific attributes of an existing item. The attributes to update are in the request body. (Note: The provided Lambda code is a simple example that only updates `name` and `price`).

#### Postman Test:
1.  Set the method to **PUT**.
2.  Set the URL to: `https://api.example.com/items/item-123`
3.  Go to the **Body** tab.
4.  Select **raw**.
5.  Select **JSON** from the dropdown.
6.  Paste the following into the body:
    ```json
    {
        "name": "Premium Blue Widget",
        "price": 24.99
    }
    ```
7.  Click **Send**.

#### `curl` Test:
```bash
curl -X PUT '[https://api.example.com/items/item-123](https://api.example.com/items/item-123)' \
-H 'Content-Type: application/json' \
-d '{
    "name": "Premium Blue Widget",
    "price": 24.99
}'
```

#### Success Response (200 OK):
```json
{
    "message": "Item updated successfully",
    "updatedAttributes": {
        "name": "Premium Blue Widget",
        "price": 24.99
    }
}
```

---

### 4. Delete (DELETE)

* **Endpoint:** `DELETE /items/{id}`
* **Action:** Deletes an item using the `id` from the URL path.

#### Postman Test:
1.  Set the method to **DELETE**.
2.  Set the URL to: `https://api.example.com/items/item-123`
3.  Click **Send**.

#### `curl` Test:
```bash
curl -X DELETE '[https://api.example.com/items/item-123](https://api.example.com/items/item-123)'
```

#### Success Response (200 OK):
```json
{
    "message": "Item deleted successfully"
}
```

---

### 5. List (GET - All Items)

* **Endpoint:** `GET /items`
* **Action:** Retrieves all items in the table.
* **⚠️ Warning:** This uses a `Scan` operation, which is inefficient and costly for large tables. Use with caution in production.

#### Postman Test:
1.  Set the method to **GET**.
2.  Set the URL to: `https://api.example.com/items`
3.  Click **Send**.

#### `curl` Test:
```bash
curl -X GET '[https://api.example.com/items](https://api.example.com/items)'
```

#### Success Response (200 OK):
```json
[
    {
        "id": "item-123",
        "name": "Premium Blue Widget",
        "price": 24.99,
        "inStock": true
    },
    {
        "id": "item-456",
        "name": "Red Sprocket",
        "price": 9.50,
        "inStock": true
    }
]
```

---

## Deployment Prerequisites

Before deploying, ensure each Lambda function has:

1.  **Correct IAM Role:** Each function must have an IAM Role with the minimum required permissions (e.g., `dynamodb:PutItem` for the create function, `dynamodb:GetItem` for the read function, etc.).
2.  **Environment Variable:** An environment variable named `TABLE_NAME` must be set, with its value being the name of your DynamoDB table.

---

## Code Details

Each Python file (`create-item-lambda.py`, `get-item-lambda.py`, etc.) contains detailed in-code comments explaining its logic.

### Key Python Concepts:

* **`boto3`:** The AWS SDK for Python, used to interact with DynamoDB.
* **`os.environ['TABLE_NAME']`:** How the Lambda function reads the environment variable to find the table.
* **`DecimalEncoder`:** A helper class used to convert DynamoDB's `Decimal` number type into a JSON-compatible `int` or `float` for API responses.
* **`parse_float=decimal.Decimal`:** Used with `json.loads()` to convert numbers *from* the incoming JSON request *into* the `Decimal` type that DynamoDB requires.