# OpenHands-Letta Integration

This integration enables OpenHands to send progress reports and updates to Letta, allowing for real-time progress tracking and communication between the two systems.

## Table of Contents
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
  - [Basic Usage](#basic-usage)
  - [Advanced Usage](#advanced-usage)
- [API Reference](#api-reference)
- [Testing](#testing)
- [Troubleshooting](#troubleshooting)

## Installation

1. Install the required packages:
```bash
pip install -r requirements.txt
```

2. Add the Letta reporter plugin to your OpenHands configuration:
```python
plugins = [
    "agent_skills.letta_reporter"
]
```

## Configuration

### Environment Variables

Create a `.env` file or set the following environment variables:

```env
LETTA_BASE_URL=https://letta2.oculair.ca
LETTA_AGENT_ID=your-agent-id
LETTA_PASSWORD=your-password
```

### Configuration Options

| Variable | Description | Default |
|----------|-------------|---------|
| LETTA_BASE_URL | Letta API base URL | https://letta2.oculair.ca |
| LETTA_AGENT_ID | Your Letta agent ID | None |
| LETTA_PASSWORD | Your Letta agent password | None |

## Usage

### Basic Usage

```python
from openhands.runtime.plugins.agent_skills.letta_reporter import LettaReporter

# Initialize the reporter
reporter = LettaReporter()

# Send a progress update
await reporter.send_progress_report(
    chat_id="chat-123",
    message_id="msg-456",
    content="Processing task: 50% complete",
    progress=0.5,
    status="in_progress"
)
```

### Advanced Usage

#### Streaming Updates

```python
async def process_task_with_updates():
    reporter = LettaReporter()
    
    # Start task
    await reporter.send_progress_report(
        chat_id="chat-123",
        message_id="msg-456",
        content="Starting task...",
        progress=0.0,
        status="in_progress"
    )
    
    # Update progress
    for i in range(5):
        progress = (i + 1) * 0.2
        await reporter.send_progress_report(
            chat_id="chat-123",
            message_id="msg-456",
            content=f"Processing step {i+1}/5...",
            progress=progress,
            status="in_progress"
        )
        await asyncio.sleep(1)  # Simulate work
    
    # Complete task
    await reporter.send_progress_report(
        chat_id="chat-123",
        message_id="msg-456",
        content="Task completed successfully!",
        progress=1.0,
        status="completed"
    )
```

#### Error Handling

```python
async def handle_task_with_errors():
    reporter = LettaReporter()
    
    try:
        # Your task code here
        raise Exception("Something went wrong")
    except Exception as e:
        await reporter.send_progress_report(
            chat_id="chat-123",
            message_id="msg-456",
            content=f"Task failed: {str(e)}",
            progress=0.0,
            status="failed"
        )
```

## API Reference

### LettaReporter Class

#### Methods

##### `send_progress_report`
Send a progress report to Letta.

Parameters:
- `chat_id` (str): The chat ID
- `message_id` (str): The message ID
- `content` (str): The progress message content
- `progress` (float, optional): Progress value between 0 and 1. Defaults to 0.0
- `status` (str, optional): Status of the task. One of: "in_progress", "completed", "failed". Defaults to "in_progress"

Returns:
- Dict containing the Letta API response

### Status Values

| Status | Description |
|--------|-------------|
| in_progress | Task is currently being processed |
| completed | Task has been completed successfully |
| failed | Task failed to complete |

## Testing

Run the integration tests:

```bash
cd tests
pytest test_letta_integration.py -v
```

### Test Configuration

1. Create a `tests/.env` file with your test credentials:
```env
LETTA_BASE_URL=https://letta2.oculair.ca
LETTA_AGENT_ID=test-agent-id
LETTA_PASSWORD=test-password
```

2. Run the tests:
```bash
python -m pytest tests/test_letta_integration.py
```

## Troubleshooting

### Common Issues

1. Connection Errors
```
Error: Could not connect to Letta API
Solution: Check your LETTA_BASE_URL and internet connection
```

2. Authentication Errors
```
Error: Invalid credentials
Solution: Verify your LETTA_AGENT_ID and LETTA_PASSWORD
```

3. Session Management
```
Error: Session already closed
Solution: Create a new LettaReporter instance for each set of reports
```

### Debug Mode

To enable debug logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This integration is part of the OpenHands project and follows its licensing terms.