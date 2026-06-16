# Simple Message System

## Description
This project is a simple message system built using FastAPI and SQLAlchemy.
It allows users to create messages to dedicated users, retrieve messages, and delete messages in bulk.
The project is structured with a clear separation of concerns, including models, schemas, repositories, services, and API routes.

## Features
- Create messages to specific users
- Retrieve unread messages
- Delete messages in bulk
- Retrieve messages with pagination

## API Endpoints
- `POST /messages/`: Create a new message.
- `GET /messages/{recipient}/unread`: Retrieve unread messages for a specific user.
- `GET /messages/{recipient}`: Retrieve messages for a specific user with pagination support.
- `DELETE /messages/{message_id}/`: Delete messages based on message ID.
- `DELETE /messages/`: Delete messages in bulk based on a list of message IDs.

## Database
The project uses PostgreSQL as the database, and SQLAlchemy is used for ORM (Object-Relational Mapping). 
The database connection URL is stored in an environment variable (`DATABASE_URL`).
## Model Description
The `Message` model represents a message in the system. It has the following fields:
- `id`: A unique identifier for the message (primary key).
  - `sender_id`: The ID of the user who sent the message in lower case.
- `recipient_id`: The ID of the user who is the recipient of the message in lower case.
- `content`: The content of the message.
- `is_read`: A boolean indicating whether the message has been read or not.
- `created_at`: A timestamp indicating when the message was created.

### composite index:
- `idx_recipient_is_read`: Index on `recipient` and `is_read` fields.
- `idx_recipient_created_at`: Index on `recipient` and `created_at` fields.

## Setup Instructions
1. Clone the repository.
2. Run `docker-compose up` to start.