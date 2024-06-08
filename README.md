# Feedback Form Popup

This project is a Python-based RESTful application that allows users to submit, retrieve, update, and delete feedback. It uses FastAPI for the backend framework and SQLAlchemy for database interactions.

## Features

- Create feedback entries
- Retrieve a specific feedback entry by ID
- Retrieve all feedback entries
- Update a feedback entry by ID
- Delete a feedback entry by ID
- Handle errors gracefully with custom exception handling
- Return data in a structured JSON format

## Technologies Used

- Python
- FastAPI
- SQLAlchemy
- PostgreSQL
- Docker

## Prerequisites

- Python 3.10 or higher
- PostgreSQL 16 or later
- Docker
- FastAPI
- SQLAlchemy (asyncpg)
- Pydantic
- Alembic
- httpx (for testing)
- unittest (for testing)

## Running the Application

1. **Clone the repository using GitHub CLI**:
    ```bash
    gh repo clone dwididit/feedback-form-popup
    cd feedback-form-popup/
    ```

2. **Create a `.env` file and configure your environment variables**:
   ```bash
    # Edit the .env file with your configuration
   DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost/feedback_form
   CORS_ORIGINS=http://localhost,http://localhost:8080,http://127.0.0.1:8080
   
   TEST_DATABASE_URL=postgresql+asyncpg://postgres:password@localhost/test_feedback_form
   
   POSTGRES_USER=postgres
   POSTGRES_PASSWORD=postgres
   POSTGRES_DB=feedback_form
   ```

3. **Build and run the application using Docker Compose**:
    ```bash
    docker compose build
    docker compose up -d
    ```

The application will run at: http://localhost:8000

To see the API endpoints using Swagger, visit: http://localhost:8000/docs

To see the API endpoints using ReDoc, visit: http://localhost:8000/redoc
   

## Running Tests

**Using `unittest` and `httpx`**
```bash
python -m unittest test_main.py
```

## API Endpoints
### Create Feedback
- Endpoint: POST /feedback/
- Description: Creates a new feedback entry.
- Request Body:
    ```json
    {
      "score": 3,
      "full_name": "John Doe",
      "email": "john.doe@example.com"
    }
    ```
- Response
    ```json
    {
      "code": 200,
      "message": "Feedback submitted successfully",
      "data": {
        "id": 1,
        "score": 3,
        "full_name": "John Doe",
        "email": "john.doe@example.com",
        "created_at": "2024-06-07T14:13:29.622188+00:00",
        "updated_at": "2024-06-07T14:13:29.622188+00:00"
      }
    }
    ```
  

### Get All Feedback
- Endpoint: GET /feedback/
- Description: Retrieves all feedback entries.
- Response:
    ```json
    {
      "code": 200,
      "message": "All feedback retrieved successfully",
      "data": [
        {
          "id": 1,
          "score": 3,
          "full_name": "John Doe",
          "email": "john.doe@example.com",
          "created_at": "2024-06-07T14:13:29.622188+00:00",
          "updated_at": "2024-06-07T14:13:29.622188+00:00"
        },
        {
          "id": 2,
          "score": 5,
          "full_name": "John Smith",
          "email": "john.doe@example.com",
          "created_at": "2024-06-07T14:13:29.622188+00:00",
          "updated_at": "2024-06-07T14:13:29.622188+00:00"
        }
      ]
    }
    ```

### Get Feedback by ID
- Endpoint: GET /feedback/{feedback_id}
- Description: Retrieves a specific feedback entry by ID.
- Response (Success):
    ```json
    {
      "code": 200,
      "message": "Feedback retrieved successfully",
      "data": {
        "id": 1,
        "score": 3,
        "full_name": "John Doe",
        "email": "john.doe@example.com",
        "created_at": "2024-06-07T14:13:29.622188+00:00",
        "updated_at": "2024-06-07T14:13:29.622188+00:00"
      }
    }
    ```
- Response (Not Found):
    ```json
    {
      "code": 500,
      "message": "404: Feedback not found",
      "data": null
    }
    ```

### Update Feedback
- Endpoint: PUT /feedback/{feedback_id}
- Description: Updates an existing feedback entry by ID.
- Request Body:
    ```json
    {
      "score": 4,
      "full_name": "John Smith",
      "email": "john.smith@example.com"
    }
    ```
- Response(Success)
    ```json
    {
      "code": 200,
      "message": "Feedback updated successfully",
      "data": {
        "id": 1,
        "score": 4,
        "full_name": "John Smith",
        "email": "john.smith@example.com",
        "created_at": "2024-06-07T14:13:29.622188+00:00",
        "updated_at": "2024-06-07T14:13:29.622188+00:00"
      }
    }
    ```
- Response(Not Found)
    ```json
    {
      "code": 500,
      "message": "404: Feedback not found",
      "data": null
    }
    ```

### Delete Feedback
- Endpoint: DELETE /feedback/{feedback_id}
- Description: Delete an existing feedback entry by ID.
- Response(Success)
```json
{
  "code": 200,
  "message": "Feedback deleted successfully",
  "data": null
}
```
- Response(Not Found)
```json
{
  "code": 500,
  "message": "404: Feedback not found",
  "data": null
}
```

## Contributing
Contributions are welcome! Please open an issue or submit a pull request for any improvements or bug fixes.