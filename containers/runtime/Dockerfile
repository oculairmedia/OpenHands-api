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
RUN curl -Ls https://micro.mamba.pm/install.sh | bash && \
    mkdir -p ~/.bashrc.d && \
    echo "export MAMBA_ROOT_PREFIX=/openhands/micromamba" >> ~/.bashrc.d/micromamba.sh && \
    echo "export PATH=/openhands/micromamba/bin:\$PATH" >> ~/.bashrc.d/micromamba.sh && \
    echo 'eval "$(micromamba shell hook --shell=bash)"' >> ~/.bashrc.d/micromamba.sh && \
    echo "source ~/.bashrc.d/micromamba.sh" >> ~/.bashrc && \
    source ~/.bashrc

# Initialize and create the conda environment
SHELL ["/bin/bash", "-c"]
RUN source ~/.bashrc && \
    micromamba create -y -n openhands -c conda-forge python=3.12 && \
    micromamba clean --all --yes

# Install Python dependencies
RUN source ~/.bashrc && \
    micromamba install -y -n openhands -c conda-forge \
    pip \
    poetry \
    && micromamba clean --all --yes

# Install additional dependencies
RUN source ~/.bashrc && \
    micromamba run -n openhands pip install \
    litellm==1.59.9 \
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
    micromamba run -n openhands poetry config virtualenvs.create false && \
    micromamba run -n openhands poetry install --no-root --no-dev

# Copy the rest of the application code
COPY --chown=openhands:openhands . .

# Install the project itself
RUN source ~/.bashrc && \
    micromamba run -n openhands poetry install --no-dev

# Environment variables for Letta
ENV LETTA_BASE_URL=https://letta2.oculair.ca
ENV LETTA_AGENT_ID=agent-b18bce75-2e73-4470-bf17-381170888a2b
ENV LETTA_PASSWORD=lettaSecurePass123
ENV LETTA_SHOW_REASONING=true
ENV LETTA_SHOW_USAGE_STATS=true

# Set default command
CMD ["bash", "-c", "source ~/.bashrc && micromamba run -n openhands python -m openhands.server.app"]
