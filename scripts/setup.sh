#!/bin/bash

# Slack MCP Server Setup Script
# This script helps you set up the Slack MCP Server

set -e

echo "🚀 Slack MCP Server Setup"
echo "========================="

# Check if Python 3.11+ is available
echo "Checking Python version..."
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.11 or higher."
    exit 1
fi

PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
REQUIRED_VERSION="3.11"

if [ "$(printf '%s\n' "$REQUIRED_VERSION" "$PYTHON_VERSION" | sort -V | head -n1)" = "$REQUIRED_VERSION" ]; then
    echo "✅ Python $PYTHON_VERSION is compatible"
else
    echo "❌ Python $PYTHON_VERSION is not compatible. Please install Python 3.11 or higher."
    exit 1
fi

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install the package
echo "Installing Slack MCP Server..."
pip install --upgrade pip
pip install -e .

# Install development dependencies if requested
if [ "$1" = "--dev" ]; then
    echo "Installing development dependencies..."
    pip install -e ".[dev]"
fi

echo ""
echo "✅ Setup completed successfully!"
echo ""
echo "Next steps:"
echo "1. Create a Slack app at https://api.slack.com/apps"
echo "2. Copy the example environment file:"
echo "   cp .env.example .env"
echo "3. Edit .env with your Slack app credentials"
echo "4. Run the OAuth flow:"
echo "   source venv/bin/activate && slack-mcp-server --oauth"
echo "5. Test the server:"
echo "   source venv/bin/activate && python examples/basic_usage.py"
echo ""
echo "For more information, see the README.md file."
