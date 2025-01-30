# Letta Reporter Plugin

This plugin enables OpenHands agents to send progress reports and updates to Letta.

## Technical Overview

The Letta Reporter plugin is implemented as an agent skill that provides asynchronous communication with the Letta API. It handles session management, authentication, and message formatting.

## Components

### LettaConfig

Configuration dataclass for storing Letta API credentials:

```python
@dataclass
class LettaConfig:
    base_url: str
    agent_id: str
    password: str
```

### LettaReporter

Main class that handles communication with Letta:

```python
class LettaReporter:
    def __init__(self)
    async def send_progress_report(self, chat_id, message_id, content, progress, status)
```

## Integration Points

### 1. Session Management

The plugin maintains an aiohttp ClientSession for efficient API communication:

```python
async def _ensure_session(self):
    if self._session is None or self._session.closed:
        self._session = aiohttp.ClientSession()
```

### 2. Authentication

Authentication is handled via HTTP headers:

```python
headers = {
    "Content-Type": "application/json",
    "X-Agent-ID": self.config.agent_id,
    "X-Agent-Password": self.config.password
}
```

### 3. Message Format

Progress reports are formatted as:

```json
{
    "chat_id": "string",
    "message_id": "string",
    "content": "string",
    "metadata": {
        "progress": float,
        "status": "string"
    }
}
```

## Plugin Registration

To register this plugin with OpenHands:

1. Add to `openhands/runtime/plugins/agent_skills/__init__.py`:
```python
from .letta_reporter import LettaReporter
```

2. Update plugin configuration:
```python
plugins = {
    "letta_reporter": LettaReporter
}
```

## API Endpoints

The plugin communicates with the following Letta API endpoints:

- `POST /api/v1/progress`: Send progress updates
- `POST /api/v1/messages`: Send general messages

## Error Handling

The plugin implements comprehensive error handling:

1. Connection errors
2. Authentication failures
3. API response errors
4. Session management issues

## Development Guidelines

When extending this plugin:

1. Maintain async/await pattern
2. Handle session cleanup
3. Implement proper error handling
4. Follow OpenHands plugin conventions

## Testing

Test files are provided in `tests/`:

```python
pytest tests/test_letta_integration.py
```

## Dependencies

- aiohttp: HTTP client
- python-dotenv: Environment management
- pytest-asyncio: Async testing

## Security Considerations

1. Credentials are stored in environment variables
2. HTTPS is enforced for API communication
3. Sessions are properly managed and cleaned up
4. Passwords are never logged

## Performance

The plugin is designed for efficient operation:

- Reuses HTTP sessions
- Implements proper cleanup
- Minimizes API calls
- Handles async operations efficiently

## Logging

Debug logging can be enabled:

```python
import logging
logging.getLogger('letta_reporter').setLevel(logging.DEBUG)
```

## Future Improvements

1. Implement rate limiting
2. Add message queuing
3. Enhance error recovery
4. Add metrics collection
5. Implement caching