# Serverless CRUD API with Lambda and DynamoDB

This project demonstrates a serverless CRUD (Create, Read, Update, Delete) backend using **Amazon API Gateway**, **AWS Lambda**, and **DynamoDB**.

The architecture follows a single-purpose function model, where each CRUD operation is handled by its own dedicated Lambda function. This approach provides better separation of concerns, easier maintenance, and more granular security and scaling.

This project consists of 5 Lambda functions:
1.  **Create:** Creates a new friend item in the DynamoDB table.
2.  **Read:** Retrieves a single friend by their `id`.
3.  **List:** Retrieves all friends from the table.
4.  **Update:** Updates specific attributes of an existing friend.
5.  **Delete:** Deletes a friend from the table.

---

## API Gateway & Test Payloads

This is an example of how your API Gateway endpoints would be configured and how you can test them using Postman or `curl`.

**Assumptions:**
* Your API Gateway endpoint is: `https://api.example.com`
* The DynamoDB table's primary key is `id` (String).
* We will use the friend's nickname (e.g., `budi`) as the unique `id`.

---

### 1. Create (POST)

* **Endpoint:** `POST /`
* **Action:** Creates a new friend. The `id` (nickname) and other attributes must be in the request body.

#### Postman Test:
1.  Set the method to **POST**.
2.  Set the URL to: `https://api.example.com`
3.  Go to the **Body** tab.
4.  Select **raw**.
5.  Select **JSON** from the dropdown.
6.  Paste the following into the body:
    ```json
    {
        "id": "budi",
        "nama_lengkap": "Budi Santoso",
        "email": "budi@example.com",
        "kota": "Jakarta"
    }
    ```
7.  Click **Send**.

#### `curl` Test:
```bash
curl -X POST 'https://api.example.com' \
-H 'Content-Type: application/json' \
-d '{
    "id": "budi",
    "nama_lengkap": "Budi Santoso",
    "email": "budi@example.com",
    "kota": "Jakarta"
}'
```

#### Success Response (201 Created):
```json
{
    "message": "Item created successfully",
    "item": {
        "id": "budi",
        "nama_lengkap": "Budi Santoso",
        "email": "budi@example.com",
        "kota": "Jakarta"
    }
}
```

---

### 2. Read (GET - Single Item)

* **Endpoint:** `GET /{id}`
* **Action:** Retrieves a single friend using their `id` (nickname) from the URL path.

#### Postman Test:
1.  Set the method to **GET**.
2.  Set the URL to: `https://api.example.com/budi`
3.  Click **Send**.

#### `curl` Test:
```bash
curl -X GET 'https://api.example.com/budi'
```

#### Success Response (200 OK):
```json
{
    "id": "budi",
    "nama_lengkap": "Budi Santoso",
    "email": "budi@example.com",
    "kota": "Jakarta"
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

* **Endpoint:** `PUT /{id}`
* **Action:** Updates specific attributes of an existing friend. (Note: The provided Lambda code is a simple example that only updates `nama_lengkap` and `kota`).

#### Postman Test:
1.  Set the method to **PUT**.
2.  Set the URL to: `https://api.example.com/budi`
3.  Go to the **Body** tab.
4.  Select **raw**.
5.  Select **JSON** from the dropdown.
6.  Paste the following into the body:
    ```json
    {
        "nama": "Budi Santoso (Updated)",
        "price": "Bandung"
    }
    ```
7.  Click **Send**.

#### `curl` Test:
```bash
curl -X PUT 'https://api.example.com/budi' \
-H 'Content-Type: application/json' \
-d '{
    "nama": "Budi Santoso (Updated)",
    "price": "Bandung"
}'
```

#### Success Response (200 OK):
```json
{
    "message": "Item updated successfully",
    "updatedAttributes": {
        "nama": "Budi Santoso (Updated)",
        "price": "Bandung"
    }
}
```

---

### 4. Delete (DELETE)

* **Endpoint:** `DELETE /{id}`
* **Action:** Deletes a friend using their `id` (nickname) from the URL path.

#### Postman Test:
1.  Set the method to **DELETE**.
2.  Set the URL to: `https://api.example.com/budi`
3.  Click **Send**.

#### `curl` Test:
```bash
curl -X DELETE 'https://api.example.com/budi'
```

#### Success Response (200 OK):
```json
{
    "message": "Item deleted successfully"
}
```

---

### 5. List (GET - All Items)

* **Endpoint:** `GET /`
* **Action:** Retrieves all friends in the table.
* **⚠️ Warning:** This uses a `Scan` operation, which is inefficient and costly for large tables. Use with caution in production.

#### Postman Test:
1.  Set the method to **GET**.
2.  Set the URL to: `https://api.example.com`
3.  Click **Send**.

#### `curl` Test:
```bash
curl -X GET 'https://api.example.com'
```

#### Success Response (200 OK):
*(Assuming you also created a friend `ani`)*
```json
[
    {
        "id": "budi",
        "nama_lengkap": "Budi Santoso (Updated)",
        "email": "budi@example.com",
        "kota": "Bandung"
    },
    {
        "id": "ani",
        "nama_lengkap": "Ani Wijaya",
        "email": "ani@example.com",
        "kota": "Surabaya"
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