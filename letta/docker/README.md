# Installing Letta Integration in Docker

## Option 1: Extend the OpenHands Docker Image

Create a custom Dockerfile that extends the base OpenHands image:

```dockerfile
# Use the official OpenHands image as base
FROM oculair/openhandsapi:latest

# Set working directory
WORKDIR /openhands/code

# Copy Letta integration files
COPY ./letta/requirements.txt /openhands/code/letta-requirements.txt
COPY ./letta/letta_openwebuifunction.py /openhands/code/letta_openwebuifunction.py
COPY ./openhands/runtime/plugins/agent_skills/letta_reporter /openhands/runtime/plugins/agent_skills/letta_reporter/

# Install Letta requirements
RUN pip install -r letta-requirements.txt

# Set Letta environment variables
ENV LETTA_BASE_URL=https://letta2.oculair.ca
ENV LETTA_AGENT_ID=your-agent-id
ENV LETTA_PASSWORD=your-password
```

## Option 2: Mount as Volume (Development)

When running the OpenHands container, mount the Letta integration as a volume:

```bash
docker run -d \
  -p 3000:3000 \
  -v $(pwd)/letta:/openhands/code/letta \
  -v $(pwd)/openhands/runtime/plugins/agent_skills/letta_reporter:/openhands/runtime/plugins/agent_skills/letta_reporter \
  -e LETTA_BASE_URL=https://letta2.oculair.ca \
  -e LETTA_AGENT_ID=your-agent-id \
  -e LETTA_PASSWORD=your-password \
  oculair/openhandsapi:latest
```

## Option 3: Using Docker Compose

Create a `docker-compose.yml` file:

```yaml
version: '3.8'

services:
  openhands:
    image: oculair/openhandsapi:latest
    ports:
      - "3000:3000"
    volumes:
      - ./letta:/openhands/code/letta
      - ./openhands/runtime/plugins/agent_skills/letta_reporter:/openhands/runtime/plugins/agent_skills/letta_reporter
    environment:
      - LETTA_BASE_URL=https://letta2.oculair.ca
      - LETTA_AGENT_ID=your-agent-id
      - LETTA_PASSWORD=your-password
```

## Installation Steps

1. Choose your preferred installation method (Options 1-3 above)

2. Update OpenHands configuration to include the Letta plugin:

Create or modify `config.toml`:
```toml
[sandbox]
plugins = [
    "agent_skills.letta_reporter"
]
```

3. Install dependencies in the container:
```bash
docker exec openhands-container pip install -r /openhands/code/letta/requirements.txt
```

4. Verify installation:
```bash
docker exec openhands-container python -c "from openhands.runtime.plugins.agent_skills.letta_reporter import LettaReporter; print('Letta plugin installed successfully')"
```

## Environment Variables

Set these environment variables when running the container:

| Variable | Description | Required |
|----------|-------------|----------|
| LETTA_BASE_URL | Letta API URL | Yes |
| LETTA_AGENT_ID | Your Letta agent ID | Yes |
| LETTA_PASSWORD | Your Letta password | Yes |

## Testing in Docker

1. Run tests inside the container:
```bash
docker exec openhands-container pytest /openhands/code/letta/tests/test_letta_integration.py
```

2. Check logs:
```bash
docker logs openhands-container
```

## Troubleshooting Docker Installation

### Common Issues

1. Plugin Not Found
```bash
# Check if plugin files are correctly mounted
docker exec openhands-container ls -l /openhands/runtime/plugins/agent_skills/letta_reporter
```

2. Dependencies Missing
```bash
# Verify requirements installation
docker exec openhands-container pip list | grep aiohttp
```

3. Permission Issues
```bash
# Fix permissions if needed
docker exec openhands-container chown -R openhands:openhands /openhands/runtime/plugins/agent_skills/letta_reporter
```

### Debug Mode

Enable debug logging in the container:

```bash
docker run -e DEBUG=true ... oculair/openhandsapi:latest
```

## Production Deployment

For production, use Option 1 (custom Dockerfile) and build your own image:

```bash
# Build custom image
docker build -t openhands-with-letta -f letta/docker/Dockerfile .

# Run container
docker run -d \
  -p 3000:3000 \
  -e LETTA_BASE_URL=https://letta2.oculair.ca \
  -e LETTA_AGENT_ID=your-agent-id \
  -e LETTA_PASSWORD=your-password \
  openhands-with-letta
```