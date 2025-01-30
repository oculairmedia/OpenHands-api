# Use the official OpenHands image as base
FROM oculair/openhandsapi:latest

# Set working directory
WORKDIR /openhands/code

# Copy Letta integration files
COPY letta/requirements.txt /openhands/code/letta-requirements.txt
COPY letta/letta_openwebuifunction.py /openhands/code/letta_openwebuifunction.py
COPY openhands/runtime/plugins/agent_skills/letta_reporter /openhands/runtime/plugins/agent_skills/letta_reporter/

# Install Letta requirements
RUN pip install -r letta-requirements.txt

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