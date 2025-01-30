import json
import requests
import os
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

def prompt_openhands(message: str, conversation_id: str = "bbeee3e2f6a94d55944dc061fdff6977") -> str:
    """
    Send a message to the OpenHands API and return the response.

    This function supports two usage scenarios:
      1) Sending a message to OpenHands and getting a response.
      2) Retrieving the tool's metadata by passing message="__tool_info__".

    If a real message is provided, this function sends it to the OpenHands API and returns 
    the response in JSON format. If the message is empty, a JSON string with an error message
    is returned. If network or HTTP errors occur, a JSON error is returned with details. The function 
    uses a retry mechanism to enhance reliability.

    Args:
        message (str):
            The message to send to OpenHands. Can also be "__tool_info__" to retrieve metadata.
        conversation_id (str, optional):
            The conversation ID to use. Defaults to "bbeee3e2f6a94d55944dc061fdff6977".

    Returns:
        str:
            - If message == "__tool_info__":
                {
                    "name": "prompt_openhands",
                    "description": "Send a message to the OpenHands API and get a response",
                    "args": {
                        "message": {
                            "type": "string",
                            "description": "The message to send or __tool_info__",
                            "required": True
                        },
                        "conversation_id": {
                            "type": "string",
                            "description": "The conversation ID to use",
                            "required": False
                        }
                    }
                }
            - Otherwise, a JSON-formatted string with either the OpenHands response or an error.

    Example:
        >>> # Sending a message to OpenHands
        >>> response = prompt_openhands("What's the capital of France?")
        >>> parsed = json.loads(response)
        >>> print(parsed)
        # Returns a dict with the OpenHands response.
    """
    # Provide tool info if message is __tool_info__
    if message == "__tool_info__":
        info = {
            "name": "prompt_openhands",
            "description": "Send a message to the OpenHands API and get a response",
            "args": {
                "message": {
                    "type": "string",
                    "description": "The message to send or __tool_info__",
                    "required": True
                },
                "conversation_id": {
                    "type": "string",
                    "description": "The conversation ID to use",
                    "required": False
                }
            }
        }
        return json.dumps(info)

    # If the message is really empty, return an error
    if not message:
        return json.dumps({"error": "Message cannot be empty"})

    base_url = os.environ.get("OPENHANDS_BASE_URL", "http://192.168.50.90:4500")

    # Prepare a session with retries
    session = requests.Session()

    payload = {
        'conversationId': conversation_id,
        'message': message
    }

    headers = {
        'Content-Type': 'application/json'
    }

    try:
        response = session.post(f"{base_url}/send-message", json=payload, headers=headers, timeout=60)
        response.raise_for_status()
        return response.text

    except requests.RequestException as e:
        return json.dumps({"error": f"Network or HTTP error - {str(e)}"})
    except Exception as e:
        return json.dumps({"error": f"Unexpected error - {str(e)}"})

if __name__ == "__main__":
    # Quick test
    test_message = "What's the capital of France, and can you multiply 7 by 8?"
    print(f"\nTesting OpenHands with message: {test_message}")
    result = prompt_openhands(test_message)
    print("\nFormatted result:")
    print(result)