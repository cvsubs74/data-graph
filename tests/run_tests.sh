#!/bin/bash

# Test Runner for Privacy Data Governance Graph Backend
# This script sets up a virtual environment and runs all tests

set -e

echo "============================================================"
echo "Privacy Data Governance Graph - Test Runner"
echo "============================================================"

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

echo "Script directory: $SCRIPT_DIR"
echo "Project root: $PROJECT_ROOT"

# Create virtual environment if it doesn't exist
VENV_DIR="$SCRIPT_DIR/venv"
if [ ! -d "$VENV_DIR" ]; then
    echo "Creating virtual environment..."
    python3 -m venv "$VENV_DIR"
    echo "✅ Virtual environment created"
else
    echo "✅ Virtual environment already exists"
fi

# Activate virtual environment
echo "Activating virtual environment..."
source "$VENV_DIR/bin/activate"

# Install/upgrade requirements
echo "Installing test requirements..."
pip install --upgrade pip
pip install -r "$SCRIPT_DIR/requirements.txt"
echo "✅ Requirements installed"

# Set PYTHONPATH to include the backend directory
export PYTHONPATH="$PROJECT_ROOT/backend:$PYTHONPATH"

echo ""
echo "============================================================"
echo "Running Tests"
echo "============================================================"

# Parse command line arguments
TEST_TYPE="${1:-all}"

case "$TEST_TYPE" in
    "integration")
        echo "Running integration tests only..."
        python3 "$SCRIPT_DIR/test_ingest_function.py"
        ;;
    "mcp")
        echo "Running MCP tests only..."
        python3 "$SCRIPT_DIR/test_mcp_server.py"
        ;;
    "all")
        echo "Running all tests..."
        echo ""
        echo "--- Ingest Function Tests ---"
        python3 "$SCRIPT_DIR/test_ingest_function.py"
        echo ""
        echo "--- MCP Server Integration Tests ---"
        python3 "$SCRIPT_DIR/test_mcp_server.py"
        ;;
    *)
        echo "Usage: $0 [unit|integration|mcp|all]"
        echo "  unit        - Run unit tests only"
        echo "  integration - Run integration tests only"
        echo "  mcp         - Run MCP tests only"
        echo "  all         - Run all tests (default)"
        exit 1
        ;;
esac

echo ""
echo "============================================================"
echo "Test run completed!"
echo "============================================================"

# Deactivate virtual environment
deactivate
