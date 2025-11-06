#!/bin/bash
# Installation script for cc-fi

set -e

echo "=== cc-fi Installation ==="
echo

# Check for Python 3.12+
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 not found. Please install Python 3.12 or higher."
    exit 1
fi

# Check for uv
if ! command -v uv &> /dev/null; then
    echo "Installing uv..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    export PATH="$HOME/.local/bin:$PATH"
fi

# Check for fzf (optional but recommended)
if ! command -v fzf &> /dev/null; then
    echo "Warning: fzf not found. Install for interactive mode (-i flag)"
    echo "  macOS: brew install fzf"
    echo "  Linux: apt install fzf"
fi

# Create virtual environment
echo "Creating virtual environment..."
uv venv

# Install package
echo "Installing cc-fi..."
source .venv/bin/activate
uv pip install -e .

# Run tests
echo "Running tests..."
if command -v pytest &> /dev/null; then
    pytest tests/unit/ -q
else
    uv pip install pytest pytest-mock
    pytest tests/unit/ -q
fi

echo
echo "Installation complete!"
echo
echo "To use cc-fi:"
echo "  1. Activate the virtual environment: source .venv/bin/activate"
echo "  2. Run: cc-fi"
echo
echo "Or add this alias to your shell profile:"
echo "  alias cc-fi='$PWD/.venv/bin/cc-fi'"
echo
