# Lightweight Ubuntu base
FROM ubuntu:22.04

# Non-interactive for apt
ENV DEBIAN_FRONTEND=noninteractive
ENV TZ=Etc/UTC

# Install dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    git \
    jq \
    unzip \
    sudo \
    python3 \
    python3-pip \
    libicu70 \
    libkrb5-3 \
    zlib1g \
    && rm -rf /var/lib/apt/lists/*

# Install Python testing tools
RUN pip install --no-cache-dir pytest httpx

# Create non-root user
RUN useradd -m runner
WORKDIR /home/runner

# Download GitHub Actions runner
ARG RUNNER_VERSION=2.328.0
RUN curl -o actions-runner-linux-x64.tar.gz -L \
    https://github.com/actions/runner/releases/download/v${RUNNER_VERSION}/actions-runner-linux-x64-${RUNNER_VERSION}.tar.gz \
    && tar xzf actions-runner-linux-x64.tar.gz \
    && rm actions-runner-linux-x64.tar.gz

# Copy entrypoint
COPY entrypoint.sh .
RUN chmod +x entrypoint.sh

# Switch to runner user
USER runner
WORKDIR /home/runner

# Entrypoint
ENTRYPOINT ["./entrypoint.sh"]