"""Command line interface for Slack MCP Server."""

import asyncio
import sys
import os
import argparse
import logging
from typing import Optional

from .server import SlackMCPServer
from .config import get_settings
from .oauth import run_oauth_flow

logger = logging.getLogger(__name__)


def setup_logging(level: str = "INFO"):
    """Setup logging configuration."""
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )


async def run_server(token: str):
    """Run the MCP server with the provided token."""
    server = SlackMCPServer(token)
    await server.run_stdio()


async def run_oauth():
    """Run the OAuth flow to get a Slack token."""
    try:
        token = await run_oauth_flow()
        if token:
            print(f"\\nOAuth successful! Your bot token is: {token}")
            print("\\nYou can now run the server with:")
            print(f"slack-mcp-server --token {token}")
            print("\\nOr set the environment variable:")
            print(f"export SLACK_BOT_TOKEN={token}")
        else:
            print("OAuth flow was cancelled or failed.")
            sys.exit(1)
    except Exception as e:
        logger.error(f"OAuth flow failed: {e}")
        sys.exit(1)


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Slack MCP Server - Model Context Protocol server for Slack integration"
    )
    
    parser.add_argument(
        "--token", 
        type=str,
        help="Slack bot token (can also be set via SLACK_BOT_TOKEN env var)"
    )
    
    parser.add_argument(
        "--oauth",
        action="store_true",
        help="Run OAuth flow to get Slack token"
    )
    
    parser.add_argument(
        "--log-level",
        type=str,
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        help="Set logging level"
    )
    
    parser.add_argument(
        "--version",
        action="version",
        version=f"Slack MCP Server {get_settings().mcp_server_version}"
    )
    
    args = parser.parse_args()
    
    # Setup logging
    setup_logging(args.log_level)
    
    # Handle OAuth flow
    if args.oauth:
        asyncio.run(run_oauth())
        return
    
    # Get token from args or environment
    token = args.token or os.getenv("SLACK_BOT_TOKEN")
    
    if not token:
        print("Error: No Slack token provided.")
        print("\\nOptions:")
        print("1. Run OAuth flow: slack-mcp-server --oauth")
        print("2. Set environment variable: export SLACK_BOT_TOKEN=your_token")
        print("3. Pass as argument: slack-mcp-server --token your_token")
        sys.exit(1)
    
    # Run the server
    try:
        asyncio.run(run_server(token))
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Server error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
