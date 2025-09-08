#!/bin/bash
set -e

# Ensure RUNNER_TOKEN and REPO_URL are provided
if [ -z "$RUNNER_TOKEN" ] || [ -z "$REPO_URL" ]; then
  echo "ERROR: RUNNER_TOKEN or REPO_URL not set"
  exit 1
fi

# Prepare MongoDB data dir in home (runner user has permissions here)
MONGO_DATA_DIR=/home/runner/data/db
MONGO_LOG=/home/runner/mongod.log
mkdir -p "$MONGO_DATA_DIR"

# Start MongoDB in the background
mongod --dbpath "$MONGO_DATA_DIR" \
       --bind_ip 127.0.0.1 \
       --port 27017 \
       --fork \
       --logpath "$MONGO_LOG"

echo "MongoDB started"

# Optional: Seed test DB
mongosh --eval 'db = db.getSiblingDB("PhotoReminder_Test"); db.createCollection("photographers"); db.createCollection("appointments"); db.createCollection("reminders");'


echo "Test DB seeded"

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

# Start the GitHub Actions runner
./run.sh
