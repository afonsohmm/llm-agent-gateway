#!/bin/bash
set -e

# Function to display usage
usage() {
    echo "Usage: $0 set <version>"
    echo "Example: $0 set 0.1.0"
    exit 1
}

# Check if the correct number of arguments is provided
if [ "$#" -ne 2 ]; then
    usage
fi

# Check if the command is "set"
if [ "$1" != "set" ]; then
    usage
fi

VERSION=$2

# Validate version format (simple validation)
if ! [[ "$VERSION" =~ ^[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
    echo "Invalid version format. Please use format X.Y.Z (e.g., 0.1.0)"
    exit 1
fi

echo "Setting application version to $VERSION..."

# --- Update pyproject.toml ---
# Using awk to find and replace the version line
awk -v ver="\"$VERSION\"" '/^version =/ {$3 = ver} {print}' pyproject.toml > pyproject.toml.tmp && mv pyproject.toml.tmp pyproject.toml
echo "Updated version in pyproject.toml"

# --- Update app/main.py ---
# Using sed to find and replace the version line
sed -i "s/^    version=\".*\",/    version=\""$VERSION\"",/" app/main.py
echo "Updated version in app/main.py"

echo "Version update complete."
