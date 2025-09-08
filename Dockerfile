# Use lightweight Ubuntu as base
FROM ubuntu:20.04

# Set non-interactive mode to avoid prompts (like tzdata)
ENV DEBIAN_FRONTEND=noninteractive
ENV TZ=Etc/UTC

# Install dependencies including MongoDB
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    git \
    jq \
    sudo \
    unzip \
    python3 \
    python3-pip \
    libicu66 \
    libkrb5-3 \
    zlib1g \
    gnupg \
    wget \
    tzdata \
    && rm -rf /var/lib/apt/lists/*

# Add MongoDB GPG key and repository
RUN wget -qO - https://www.mongodb.org/static/pgp/server-6.0.asc | apt-key add - \
    && echo "deb [ arch=amd64,arm64 ] https://repo.mongodb.org/apt/ubuntu focal/mongodb-org/6.0 multiverse" | tee /etc/apt/sources.list.d/mongodb-org-6.0.list

# Install MongoDB
RUN apt-get update && apt-get install -y mongodb-org && rm -rf /var/lib/apt/lists/*
RUN apt-get install -y mongodb-mongosh mongodb-database-tools
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

RUN mkdir -p /data/db && chown -R runner:runner /data/db
# Switch to runner user
USER runner
WORKDIR /home/runner

# Expose MongoDB default port
EXPOSE 27017

# Entrypoint will configure & start runner
ENTRYPOINT ["./entrypoint.sh"]
