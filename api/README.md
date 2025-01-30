# OpenHands API

This API provides a RESTful interface to interact with OpenHands AI agents. It enables users to create interactive sessions, send messages, and manage conversations with OpenHands agents.

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run the API server:
```bash
uvicorn main:app --reload
```

The API will be available at `http://localhost:8000`

## API Documentation

### Authentication

All API endpoints require an authentication token passed in the `Authorization` header. For testing purposes, any non-empty Bearer token will work.

Example:
```http
Authorization: Bearer test-token
```

You can also use a simple token without the Bearer prefix:
```http
Authorization: test-token
```

### Endpoints

#### Create Session
```http
POST /sessions
```

Create a new interactive session with OpenHands.

**Request Body:**
```json
{
    "github_token": "optional-github-token",
    "selected_repository": "optional-repository-name",
    "initial_message": "optional-first-message"
}
```

**Response:**
```json
{
    "conversation_id": "unique-conversation-id",
    "status": "ok"
}
```

#### Real-time Communication
```http
WebSocket /ws/{conversation_id}
```

Connect to a WebSocket for real-time message exchange with OpenHands.

**Send Message:**
```json
"Your message here"
```

**Receive Response:**
```json
{
    "events": [
        {
            "type": "message",
            "content": "Agent's response"
        }
    ],
    "has_more": false
}
```

**Error Response:**
```json
{
    "error": true,
    "message": "Error description"
}
```

**WebSocket Close Codes:**
- 4000: General error
- 4001: Invalid authentication token
- 4004: Conversation not found

#### End Session
```http
DELETE /sessions/{conversation_id}
```

End an interactive session.

**Response:**
```json
{
    "status": "success",
    "message": "Session ended successfully"
}
```

### Error Handling

The API uses standard HTTP status codes and returns error messages in the following format:

```json
{
    "error": true,
    "message": "Error description",
    "status_code": 400
}
```

Common status codes:
- 400: Bad Request
- 401: Unauthorized
- 404: Not Found
- 500: Internal Server Error

## Example Usage

```python
import asyncio
import websockets
import requests
import json

# Configuration
API_BASE_URL = "http://localhost:8000"
WS_BASE_URL = "ws://localhost:8000"
AUTH_TOKEN = "your-auth-token"
HEADERS = {"Authorization": AUTH_TOKEN}

async def chat_with_agent():
    # Create a session
    session_response = requests.post(
        f"{API_BASE_URL}/sessions",
        headers=HEADERS,
        json={
            "initial_message": "Hello, I need help with my code"
        }
    )
    conversation_id = session_response.json()["conversation_id"]

    try:
        # Connect to WebSocket
        async with websockets.connect(
            f"{WS_BASE_URL}/ws/{conversation_id}",
            extra_headers=HEADERS
        ) as websocket:
            # Send a message
            await websocket.send("Can you help me optimize this function?")
            
            # Receive response
            response = await websocket.recv()
            data = json.loads(response)
            
            if "error" in data:
                print(f"Error: {data['message']}")
            else:
                for event in data["events"]:
                    if event["type"] == "message":
                        print(f"Agent: {event['content']}")
    
    finally:
        # End the session
        requests.delete(
            f"{API_BASE_URL}/sessions/{conversation_id}",
            headers=HEADERS
        )

# Run the async function
asyncio.run(chat_with_agent())
```

Note: You'll need to install the `websockets` package:
```bash
pip install websockets