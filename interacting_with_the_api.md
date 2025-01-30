# Interacting with the OpenHands API

This document outlines the methods and commands for interacting with the OpenHands API.

## Docker Image

The OpenHands API is available as a Docker image on DockerHub. You can pull the image using the following command:

```bash
docker pull oculair/openhandsapi:latest
```

To run the container:

```bash
docker run -d -p 3000:3000 --name openhands-container oculair/openhandsapi:latest
```

This will start the OpenHands API server on your local machine, accessible at `http://localhost:3000`.

### Using Docker Compose

Alternatively, you can use Docker Compose to run the OpenHands API. A `compose.yml` file is provided in the `scripts` folder. To use it:

1. Download the `compose.yml` file from the `scripts` folder of the OpenHands repository.

2. In the directory where you saved the `compose.yml` file, run the following command:
   ```bash
   docker-compose up -d
   ```

This will pull the OpenHands API image from Docker Hub and start the server using the configuration specified in the `compose.yml` file.

Note: This method does not require any local setup or file structure. The Docker image contains all necessary files and configurations.

## API Endpoint

The API endpoint for sending messages to OpenHands is:

```
http://localhost:3000/send-message
```

## Making a Request

To interact with the OpenHands API, you need to send a POST request with a JSON body containing the `conversationId` and `message`.

### Using PowerShell

Here's an example of how to send a request using PowerShell:

```powershell
$body = @{
    conversationId = "bbeee3e2f6a94d55944dc061fdff6977"
    message = "Your message here"
} | ConvertTo-Json

$headers = @{
    "Content-Type" = "application/json"
}

$response = Invoke-WebRequest -Uri "http://localhost:3000/send-message" -Method Post -Body $body -Headers $headers -UseBasicParsing

# Display the response
Write-Output "Response Content:"
$response.Content | ConvertFrom-Json | ConvertTo-Json -Depth 10
```

Replace "Your message here" with the actual message you want to send to OpenHands.

## Response Format

The API returns a JSON response with the following structure:

```json
{
    "response": {
        "id": number,
        "timestamp": string,
        "source": string,
        "message": string,
        "action": string,
        "args": {
            "content": string,
            "image_urls": null | array,
            "wait_for_response": boolean
        }
    }
}
```

The `message` field in the response contains OpenHands' reply to your input.

## Example

Here's an example of sending a message and the response you might receive:

Request:
```powershell
$body = @{
    conversationId = "bbeee3e2f6a94d55944dc061fdff6977"
    message = "Hello OpenHands, can you please calculate the sum of 15 and 27, and then tell me what day of the week it is today?"
} | ConvertTo-Json

# ... (rest of the PowerShell code as shown above)
```

Response:
```json
{
    "response": {
        "id": 95,
        "timestamp": "2025-01-26T03:38:52.697752",
        "source": "agent",
        "message": "So:\n1. 15 + 27 = 42\n2. Today is Sunday",
        "action": "message",
        "args": {
            "content": "So:\n1. 15 + 27 = 42\n2. Today is Sunday",
            "image_urls": null,
            "wait_for_response": true
        }
    }
}
```

## Using the Python Tool

We've provided a Python script `prompt_openhands.py` in the `scripts` folder that simplifies interaction with the OpenHands API. Here's how to use it:

1. Ensure you have Python installed on your system.
2. Install the required packages:
   ```
   pip install requests
   ```
3. Navigate to the `scripts` folder:
   ```
   cd openhands-repo/scripts
   ```
4. Run the script:
   ```
   python prompt_openhands.py
   ```

You can also import and use the `prompt_openhands` function in your Python scripts:

```python
from prompt_openhands import prompt_openhands

response = prompt_openhands("What's the capital of France, and can you multiply 7 by 8?")
print(response)
```

The `prompt_openhands` function accepts two parameters:
- `message` (required): The message to send to OpenHands.
- `conversation_id` (optional): The conversation ID to use. Defaults to "bbeee3e2f6a94d55944dc061fdff6977".

This document should help users interact with the OpenHands API effectively using both PowerShell and the provided Python tool.