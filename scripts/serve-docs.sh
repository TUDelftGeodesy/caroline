#!/usr/bin/env bash
set -euo pipefail

# Determine the repository root, regardless of where the script is called.
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

# Make custom MkDocs modules (e.g. docs_hooks.py) importable.
export PYTHONPATH="$REPO_ROOT${PYTHONPATH:+:$PYTHONPATH}"

# Build and validate documentation.
echo "Building documentation..."
mkdocs build --clean --strict

# Start the local documentation server.
echo "Starting MkDocs server..."
exec mkdocs serve