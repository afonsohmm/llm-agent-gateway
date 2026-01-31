#!/bin/bash
set -e

echo "Starting LLM Agent Gateway and Ollama containers..."

# Extract version from pyproject.toml
export GATEWAY_VERSION=$(grep -m 1 '^version =' pyproject.toml | awk '{print $3}' | tr -d '"')

if [ -z "$GATEWAY_VERSION" ]; then
    echo "Error: Version could not be found in pyproject.toml"
    exit 1
fi

echo "Running version: $GATEWAY_VERSION"

docker-compose up -d --force-recreate gateway

echo "Containers started. Access the gateway at http://localhost:8000"
