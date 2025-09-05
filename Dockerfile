# Use lightweight Ubuntu as base
FROM ubuntu:22.04

RUN apt-get update && apt-get install -y \
    curl \
    git \
    jq \
    sudo \
    unzip \
    python3 \
    python3-pip \
    libicu70 \
    libkrb5-3 \
    zlib1g \
    && rm -rf /var/lib/apt/lists/*

# Create a non-root user for the runner
RUN useradd -m runner
WORKDIR /home/runner

# Download and extract GitHub Actions runner
ARG RUNNER_VERSION=2.328.0
ARG RUNNER_SHA256=01066fad3a2893e63e6ca880ae3a1fad5bf9329d60e77ee15f2b97c148c3cd4e

RUN curl -o actions-runner-linux-x64.tar.gz -L https://github.com/actions/runner/releases/download/v${RUNNER_VERSION}/actions-runner-linux-x64-${RUNNER_VERSION}.tar.gz \
    && echo "${RUNNER_SHA256}  actions-runner-linux-x64.tar.gz" | sha256sum -c - \
    && tar xzf actions-runner-linux-x64.tar.gz \
    && rm actions-runner-linux-x64.tar.gz

# Copy entrypoint script
COPY entrypoint.sh .
RUN chmod +x entrypoint.sh

# Switch to runner user
USER runner
WORKDIR /home/runner

# Entrypoint will configure & start runner
ENTRYPOINT ["./entrypoint.sh"]
