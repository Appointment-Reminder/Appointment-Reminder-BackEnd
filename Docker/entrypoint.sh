#!/bin/bash
set -e

# Ensure required environment variables
if [ -z "$RUNNER_TOKEN" ] || [ -z "$REPO_URL" ]; then
  echo "ERROR: RUNNER_TOKEN or REPO_URL not set"
  exit 1
fi

# Dynamic runner name and labels
RUNNER_NAME="${RUNNER_NAME:-docker-runner}"
RUNNER_LABELS="${RUNNER_LABELS:-docker,linux}"

# Configure runner if not already configured
if [ ! -f .runner ]; then
  ./config.sh --url "$REPO_URL" \
              --token "$RUNNER_TOKEN" \
              --name "$RUNNER_NAME" \
              --labels "$RUNNER_LABELS" \
              --work _work \
              --unattended \
              --replace
  touch .runner
fi

# Start the runner
./run.sh
