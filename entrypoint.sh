#!/bin/bash
set -e

# Ensure RUNNER_TOKEN and REPO_URL are provided
if [ -z "$RUNNER_TOKEN" ] || [ -z "$REPO_URL" ]; then
  echo "ERROR: RUNNER_TOKEN or REPO_URL not set"
  exit 1
fi

# Configure the runner only if not already configured
if [ ! -f .runner ]; then
  ./config.sh --url "$REPO_URL" \
              --token "$RUNNER_TOKEN" \
              --name docker-runner \
              --work _work \
              --unattended \
              --replace
  touch .runner
fi

# Start the runner
./run.sh
