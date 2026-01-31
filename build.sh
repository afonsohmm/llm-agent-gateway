#!/bin/bash
set -e

echo "Building Docker image for LLM Agent Gateway..."

# Extract version from pyproject.toml
VERSION=$(grep -m 1 '^version =' pyproject.toml | awk '{print $3}' | tr -d '"')

if [ -z "$VERSION" ]; then
    echo "Error: Version could not be found in pyproject.toml"
    exit 1
fi

echo "Building version: $VERSION"

# Build and tag the image
docker build -t llm-agent-gateway:$VERSION .

echo "Docker image llm-agent-gateway:$VERSION built successfully."
