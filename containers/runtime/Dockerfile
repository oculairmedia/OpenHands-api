FROM ubuntu:22.04

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV OPENHANDS_HOME=/openhands
ENV MAMBA_ROOT_PREFIX=/openhands/micromamba
ENV MAMBA_EXE=/openhands/micromamba/bin/micromamba
ENV PATH="/openhands/micromamba/bin:${PATH}"

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    curl \
    wget \
    bzip2 \
    && rm -rf /var/lib/apt/lists/*

# Create openhands user and directories
RUN useradd -ms /bin/bash openhands && \
    mkdir -p /openhands/micromamba/bin && \
    chown -R openhands:openhands /openhands

USER openhands
WORKDIR /openhands

# Install micromamba
RUN cd /openhands/micromamba/bin && \
    wget -q https://micro.mamba.pm/api/micromamba/linux-64/latest -O - | tar -xj && \
    chmod +x micromamba && \
    ./micromamba shell init -s bash -p /openhands/micromamba && \
    echo "source /openhands/micromamba/etc/profile.d/micromamba.sh" >> ~/.bashrc

# Initialize and create the conda environment
SHELL ["/bin/bash", "-c"]
RUN source ~/.bashrc && \
    eval "$(micromamba shell hook --shell=bash)" && \
    micromamba create -n openhands python=3.12 -c conda-forge -y && \
    micromamba activate openhands

# Install Python dependencies
RUN source ~/.bashrc && \
    eval "$(micromamba shell hook --shell=bash)" && \
    micromamba activate openhands && \
    micromamba install -n openhands -c conda-forge \
    pip \
    poetry \
    && micromamba clean --all --yes

# Install additional dependencies
RUN source ~/.bashrc && \
    eval "$(micromamba shell hook --shell=bash)" && \
    micromamba activate openhands && \
    pip install litellm==1.59.9 \
    termcolor==2.5.0 \
    aiohttp==3.11.11 \
    pydantic==2.10.4 \
    python-dotenv \
    typing-extensions \
    pydantic-core \
    annotated-types \
    yarl \
    multidict \
    frozenlist \
    attrs \
    charset-normalizer

# Create project structure
RUN mkdir -p /openhands/app
WORKDIR /openhands/app

# Copy only dependency files first
COPY --chown=openhands:openhands pyproject.toml poetry.lock ./

# Create empty README.md (required by poetry)
RUN touch README.md

# Install dependencies only
RUN source ~/.bashrc && \
    eval "$(micromamba shell hook --shell=bash)" && \
    micromamba activate openhands && \
    poetry config virtualenvs.create false && \
    poetry install --no-root --no-dev

# Copy the rest of the application code
COPY --chown=openhands:openhands . .

# Install the project itself
RUN source ~/.bashrc && \
    eval "$(micromamba shell hook --shell=bash)" && \
    micromamba activate openhands && \
    poetry install --no-dev

# Environment variables for Letta
ENV LETTA_BASE_URL=https://letta2.oculair.ca
ENV LETTA_AGENT_ID=agent-b18bce75-2e73-4470-bf17-381170888a2b
ENV LETTA_PASSWORD=lettaSecurePass123
ENV LETTA_SHOW_REASONING=true
ENV LETTA_SHOW_USAGE_STATS=true

# Set default command
CMD ["bash", "-c", "source ~/.bashrc && eval \"$(micromamba shell hook --shell=bash)\" && micromamba activate openhands && python -m openhands.server.app"]
