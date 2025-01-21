import asyncio
import websockets
import requests
import json
import sys
import time

# Configuration
API_BASE_URL = "http://localhost:8001"
WS_BASE_URL = "ws://localhost:8001"
AUTH_TOKEN = "test-token"
HEADERS = {
    "Authorization": f"Bearer {AUTH_TOKEN}",
    "Content-Type": "application/json"
}

# Endpoints
API_PREFIX = "/api/v1"
HEALTH_URL = f"{API_BASE_URL}/health"

# API endpoints
CREATE_SESSION_ENDPOINT = f"{API_PREFIX}/conversations"
WEBSOCKET_ENDPOINT = f"{API_PREFIX}/conversations/{{conversation_id}}/events/ws"
DELETE_SESSION_ENDPOINT = f"{API_PREFIX}/conversations/{{conversation_id}}"

def check_api_status():
    """Check if our API is accessible"""
    try:
        response = requests.get(HEALTH_URL)
        if response.status_code == 200:
            print("✓ API is running")
            return True
        else:
            print(f"✗ API returned status code: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("✗ Could not connect to API")
        return False

async def chat_with_agent():
    try:
        # Step 1: Create a session
        print("\nCreating session...")
        request_url = f"{API_BASE_URL}{CREATE_SESSION_ENDPOINT}"
        print(f"\nRequest URL: {request_url}")
        session_response = requests.post(
            request_url,
            headers=HEADERS,
            json={
                "github_token": None,
                "selected_repository": None
            }
        )
        
        if session_response.status_code != 200:
            print(f"Error creating session: {session_response.text}")
            print(f"Status code: {session_response.status_code}")
            print(f"Response headers: {session_response.headers}")
            return
            
        response_data = session_response.json()
        conversation_id = response_data["conversation_id"]
        print(f"Session created successfully. Conversation ID: {conversation_id}")

        # Step 2: Connect to WebSocket
        print("\nConnecting to WebSocket...")
        ws_url = f"{WS_BASE_URL}{WEBSOCKET_ENDPOINT.format(conversation_id=conversation_id)}"
        print(f"WebSocket URL: {ws_url}")
        
        async with websockets.connect(ws_url) as websocket:
            # Send headers in a message
            await websocket.send(json.dumps({"type": "auth", "headers": HEADERS}))
            print("WebSocket connected successfully")
            
            # Step 3: Send a test message
            test_message = "Can you help me write a function to calculate fibonacci numbers?"
            print(f"\nSending message: {test_message}")
            await websocket.send(test_message)
            
            # Step 4: Receive and process response
            print("\nWaiting for response...")
            try:
                # Set up a task to receive the response
                response_task = asyncio.create_task(websocket.recv())
                
                # Wait for response with timeout
                response = await asyncio.wait_for(response_task, timeout=5.0)
                data = json.loads(response)
                
                if "error" in data:
                    print(f"Error: {data['message']}")
                else:
                    print("\nReceived response:")
                    for event in data["events"]:
                        if event["type"] == "message":
                            print(f"Agent: {event['content']}")
                
                # Wait a moment to ensure response is fully processed
                await asyncio.sleep(0.5)
                
            except asyncio.TimeoutError:
                print("\nTimeout waiting for response")
            except Exception as e:
                print(f"\nError receiving response: {e}")
            finally:
                try:
                    await websocket.close()
                except:
                    pass
    
    except websockets.exceptions.WebSocketException as e:
        print(f"\nWebSocket error: {e}")
    except requests.exceptions.RequestException as e:
        print(f"\nHTTP request error: {e}")
    except Exception as e:
        print(f"\nUnexpected error: {e}")
    
    finally:
        # Step 5: End the session
        if 'conversation_id' in locals():
            try:
                print(f"\nEnding session {conversation_id}...")
                end_response = requests.delete(
                    f"{API_BASE_URL}{DELETE_SESSION_ENDPOINT.format(conversation_id=conversation_id)}",
                    headers=HEADERS
                )
                if end_response.status_code == 200:
                    print("Session ended successfully")
                else:
                    print(f"Error ending session: {end_response.text}")
            except Exception as e:
                print(f"Error while ending session: {e}")

if __name__ == "__main__":
    print("Starting API test...")
    print("\nChecking API status...")
    if not check_api_status():
        print("\nERROR: API is not accessible.")
        print("Make sure the server is running and accessible at http://localhost:8001")
        sys.exit(1)
        
    print("\nAPI is accessible, proceeding with test...")
    try:
        asyncio.run(chat_with_agent())
    except KeyboardInterrupt:
        print("\nTest interrupted by user")
    except Exception as e:
        print(f"Error running test: {e}")