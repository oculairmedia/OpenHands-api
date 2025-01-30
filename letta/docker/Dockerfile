# Use the official OpenHands image as base
FROM oculair/openhandsapi:latest

# Set working directory
WORKDIR /openhands/code

# Copy and install requirements first
COPY letta/requirements.txt /tmp/letta-requirements.txt
RUN pip install -r /tmp/letta-requirements.txt

# Copy remaining Letta integration files
COPY letta/letta_openwebuifunction.py /openhands/code/letta_openwebuifunction.py
COPY openhands/runtime/plugins/agent_skills/letta_reporter /openhands/runtime/plugins/agent_skills/letta_reporter/

# Set default environment variables (can be overridden at runtime)
ENV LETTA_BASE_URL=https://letta2.oculair.ca
ENV LETTA_AGENT_ID=""
ENV LETTA_PASSWORD=""

# Create config directory if it doesn't exist
RUN mkdir -p /openhands/config

# Add Letta plugin to OpenHands configuration
RUN echo '[sandbox]\nplugins = ["agent_skills.letta_reporter"]' >> /openhands/config/config.toml

# Set permissions
RUN chown -R openhands:openhands /openhands/runtime/plugins/agent_skills/letta_reporter