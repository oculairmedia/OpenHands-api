from fastapi import FastAPI, HTTPException, Header, Request, WebSocket, WebSocketDisconnect, Depends
import logging
import time
import json
import uuid
import asyncio
from typing import Dict, Optional
from pydantic import BaseModel

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="OpenHands API",
    description="API for interacting with OpenHands AI agents",
    version="1.0.0"
)

# Active sessions store
active_sessions: Dict[str, dict] = {}

class ConversationRequest(BaseModel):
    github_token: Optional[str] = None
    selected_repository: Optional[str] = None

# Debug middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all incoming requests"""
    logger.info("=== Incoming Request ===")
    logger.info(f"Method: {request.method}")
    logger.info(f"URL: {request.url}")
    logger.info(f"Path: {request.url.path}")
    logger.info(f"Headers: {dict(request.headers)}")
    try:
        response = await call_next(request)
        logger.info("=== Response ===")
        logger.info(f"Status: {response.status_code}")
        return response
    except Exception as e:
        logger.error(f"Error processing request: {str(e)}")
        raise

async def get_token_header(authorization: str = Header(...)) -> str:
    """Validate authorization header"""
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid authorization header")
    token = authorization.replace("Bearer ", "")
    return token

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": time.time()}

@app.post("/api/v1/conversations")
async def create_conversation(
    request: ConversationRequest,
    authorization: str = Header(...)
):
    """Create a new conversation session"""
    token = authorization.replace("Bearer ", "")
    conversation_id = str(uuid.uuid4())
    active_sessions[conversation_id] = {
        "token": token,
        "github_token": request.github_token,
        "selected_repository": request.selected_repository,
        "created_at": time.time()
    }
    logger.info(f"Created new conversation session: {conversation_id}")
    return {"conversation_id": conversation_id}

@app.websocket("/api/v1/conversations/{conversation_id}/events/ws")
async def conversation_websocket(
    websocket: WebSocket,
    conversation_id: str,
):
    """WebSocket endpoint for real-time conversation events"""
    try:
        await websocket.accept()
        
        # Wait for auth message
        auth_message = await websocket.receive_text()
        try:
            auth_data = json.loads(auth_message)
            if auth_data.get("type") != "auth":
                await websocket.close(code=4001, reason="Expected auth message")
                return
                
            headers = auth_data.get("headers", {})
            auth_header = headers.get("Authorization")
            if not auth_header or not auth_header.startswith("Bearer "):
                await websocket.close(code=4001, reason="Unauthorized")
                return
                
            token = auth_header.replace("Bearer ", "")
        except json.JSONDecodeError:
            await websocket.close(code=4001, reason="Invalid auth message")
            return
        
        # Validate conversation exists and token matches
        if conversation_id not in active_sessions:
            await websocket.close(code=4004, reason="Conversation not found")
            return
            
        if active_sessions[conversation_id]["token"] != token:
            await websocket.close(code=4003, reason="Invalid token")
            return

        await websocket.accept()
        logger.info(f"WebSocket connected for conversation: {conversation_id}")

        try:
            # Create an event to signal when response is sent
            response_sent = asyncio.Event()

            # Receive message from client
            message = await websocket.receive_text()
            logger.info(f"Received message in conversation {conversation_id}: {message}")

            # Simulate agent response
            response = {
                "events": [
                    {
                        "type": "message",
                        "content": f"I received your message: {message}\nHere's a sample Fibonacci function:\n\ndef fibonacci(n):\n    if n <= 1:\n        return n\n    return fibonacci(n-1) + fibonacci(n-2)"
                    }
                ]
            }
            
            # Send response
            await websocket.send_text(json.dumps(response))
            response_sent.set()

            # Wait for a moment to ensure client receives response
            await asyncio.sleep(0.5)

        except Exception as e:
            logger.error(f"Error in WebSocket communication: {str(e)}")
            raise

    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected for conversation: {conversation_id}")
    except Exception as e:
        logger.error(f"WebSocket error in conversation {conversation_id}: {str(e)}")
        try:
            await websocket.close(code=4000, reason="Internal server error")
        except:
            pass

@app.delete("/api/v1/conversations/{conversation_id}")
async def delete_conversation(
    conversation_id: str,
    authorization: str = Header(...)
):
    """Delete a conversation session"""
    token = authorization.replace("Bearer ", "")
    if conversation_id not in active_sessions:
        raise HTTPException(status_code=404, detail="Conversation not found")
        
    if active_sessions[conversation_id]["token"] != token:
        raise HTTPException(status_code=403, detail="Invalid token")
        
    del active_sessions[conversation_id]
    logger.info(f"Deleted conversation session: {conversation_id}")
    return {"status": "success"}
