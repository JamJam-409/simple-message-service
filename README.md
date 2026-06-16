# Simple Message System

## Description
This project is a simple message system built using FastAPI and SQLAlchemy.
It allows users to create messages to dedicated users, retrieve messages, and delete messages in bulk.
The project is structured with a clear separation of concerns, including models, schemas, repositories, services, and API routes.

## Features
- Create messages to specific users
- Retrieve unread messages
- Delete messages by id and in bulk
- Retrieve messages with pagination

## Assumptions
- Recipient identifiers are case-insensitive (stored as lowercase). "Alice" and "alice" are the
same user.
- No authentication — the recipient in the URL identifies the user.
- "Fetch unread" marks messages as read atomically (single DB operation). This prevents
duplicate delivery under concurrent access.
- Start/stop index uses offset-based pagination on time-ordered results. When there's a timestamp collision use message id for ordering.
- Message content is plain text with a 5000-character limit.
- Bulk delete is capped at 100 IDs per request.
    
## API Endpoints
- `POST /messages/`: Create a new message.
- `GET /messages/{recipient}/unread`: Retrieve unread messages for a specific user. **When getting unread messages, the messages will be marked as read and won't be returned in subsequent requests.**
- `GET /messages/{recipient}`: Retrieve messages for a specific user with pagination support.
- `DELETE /messages/{message_id}/`: Delete messages based on message ID.
- `DELETE /messages/`: Delete messages in bulk based on a list of message IDs.

## Database
The project uses PostgreSQL as the database, and SQLAlchemy is used for ORM (Object-Relational Mapping). 
The database connection URL is stored in an environment variable (`DATABASE_URL`).
## Model Description
The `Message` model represents a message in the system. It has the following fields:
- `id`: A unique identifier for the message (primary key).
- `sender`: The ID of the user who sent the message in lower case.
- `recipient`: The ID of the user who is the recipient of the message in lower case.
- `content`: The content of the message.
- `is_read`: A boolean indicating whether the message has been read or not.
- `created_at`: A UTC timestamp indicating when the message was created.

### composite index:
- `idx_recipient_is_read`: Index on `recipient` and `is_read` fields.
- `idx_recipient_created_at`: Index on `recipient` and `created_at` fields.

## Setup Instructions
1. Clone the repository.
2. Run 
```bash
  docker-compose up --build
  ```
### Curl examples
```bash
  # create
  curl -X POST localhost:8000/messages/ -H 'Content-Type: application/json' \
    -d '{"sender":"bob","recipient":"alice","content":"hello"}'
  # unread (marks read)
  curl localhost:8000/messages/alice/unread
  # by index (time-ordered)
  curl 'localhost:8000/messages/alice?start_index=0&stop_index=10'
  # delete one
  curl -X DELETE localhost:8000/messages/<uuid>
  # bulk delete
  curl -X DELETE localhost:8000/messages/ -H 'Content-Type: application/json' \
    -d '{"message_ids":["<uuid1>","<uuid2>"]}'
  ```
**Also possible to test using Swagger UI by visiting [localhost:8000/docs](localhost:8000/docs)**

## Running Unit Tests & IT
Tests are excluded from docker image and executed by Github Actions when pushing and making pull requests.
To run the tests locally,
```bash
pip install -r requirements-test.txt
DATABASE_URL=postgresql+psycopg2://postgres:postgres@localhost:5432/messages pytest test/ -v
```

## Future: CI/CD and Deployment
Some ideas of further development for this project since time to implement is limited.

### Docker Image Publishing
A GitHub Actions workflow would build and push the Docker image to Docker Hub on every push to
`main`.
Requires `DOCKERHUB_USERNAME` and `DOCKERHUB_TOKEN` configured as repository secrets.

### Kubernetes Deployment
The service would be deployed on Kubernetes with:
- **API Deployment** (2+ replicas) behind a LoadBalancer Service for high availability. 
- **PostgreSQL** with read replicas for scaling read-heavy queries (message retrieval by
index). Write operations (create, delete, mark-as-read) go to the primary; reads can be routed
to replicas.
- Alembic migrations run as an init container before the API pods start, ensuring schema
consistency on deploy.
