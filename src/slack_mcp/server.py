"""Main MCP server implementation for Slack integration."""

import asyncio
import logging
from typing import Any, Sequence
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import (
    Resource, 
    Tool, 
    TextResourceContents,
    CallToolResult,
    ListResourcesResult,
    ListToolsResult,
    ReadResourceResult
)

from .config import get_settings
from .slack_client import SlackClient, SlackClientError
from .handlers.resources import ResourceHandler
from .handlers.tools import ToolHandler

logger = logging.getLogger(__name__)


class SlackMCPServer:
    """Main Slack MCP Server class."""
    
    def __init__(self, slack_token: str):
        """Initialize the Slack MCP server."""
        self.slack_client = SlackClient(slack_token)
        self.resource_handler = ResourceHandler(self.slack_client)
        self.tool_handler = ToolHandler(self.slack_client)
        
        # Create MCP server
        settings = get_settings()
        self.server = Server(settings.mcp_server_name, settings.mcp_server_version)
        self._setup_handlers()
    
    def _setup_handlers(self):
        """Set up MCP server handlers."""
        
        @self.server.list_resources()
        async def handle_list_resources() -> ListResourcesResult:
            """Handle list resources request."""
            try:
                resources = await self.resource_handler.list_resources()
                return ListResourcesResult(resources=resources, nextCursor=None)
            except Exception as e:
                logger.error(f"Error listing resources: {e}")
                return ListResourcesResult(resources=[], nextCursor=None)
        
        @self.server.read_resource()
        async def handle_read_resource(uri: str) -> ReadResourceResult:
            """Handle read resource request."""
            try:
                content = await self.resource_handler.read_resource(uri)
                return ReadResourceResult(
                    contents=[
                        TextResourceContents(
                            uri=uri,
                            mimeType="application/json" if uri != "slack://error" else "text/plain",
                            text=content if isinstance(content, str) else content.decode()
                        )
                    ]
                )
            except Exception as e:
                logger.error(f"Error reading resource {uri}: {e}")
                return ReadResourceResult(
                    contents=[
                        TextResourceContents(
                            uri=uri,
                            mimeType="text/plain",
                            text=f"Error reading resource: {e}"
                        )
                    ]
                )
        
        @self.server.list_tools()
        async def handle_list_tools() -> ListToolsResult:
            """Handle list tools request."""
            try:
                tools = self.tool_handler.list_tools()
                return ListToolsResult(tools=tools, nextCursor=None)
            except Exception as e:
                logger.error(f"Error listing tools: {e}")
                return ListToolsResult(tools=[], nextCursor=None)
        
        @self.server.call_tool()
        async def handle_call_tool(name: str, arguments: dict[str, Any] | None) -> CallToolResult:
            """Handle tool call request."""
            try:
                result = await self.tool_handler.call_tool(name, arguments or {})
                return CallToolResult(
                    content=result.content,
                    isError=result.is_error
                )
            except Exception as e:
                logger.error(f"Error calling tool {name}: {e}")
                return CallToolResult(
                    content=[{
                        "type": "text",
                        "text": f"Error calling tool: {e}"
                    }],
                    isError=True
                )
    
    async def test_connection(self) -> bool:
        """Test the Slack connection."""
        try:
            auth_info = await self.slack_client.test_auth()
            logger.info(f"Connected to Slack as {auth_info.get('user')} in team {auth_info.get('team')}")
            return True
        except SlackClientError as e:
            logger.error(f"Failed to connect to Slack: {e}")
            return False
    
    async def run_stdio(self):
        """Run the server using stdio transport."""
        settings = get_settings()
        logger.info(f"Starting {settings.mcp_server_name} v{settings.mcp_server_version}")
        
        # Test connection first
        if not await self.test_connection():
            logger.error("Failed to connect to Slack. Please check your token.")
            return
        
        # Run the server
        async with stdio_server() as (read_stream, write_stream):
            await self.server.run(
                read_stream,
                write_stream,
                self.server.create_initialization_options()
            )


async def main():
    """Main entry point for the MCP server."""
    import sys
    
    # Get Slack token from environment or command line
    slack_token = None
    
    if len(sys.argv) > 1:
        slack_token = sys.argv[1]
    else:
        import os
        slack_token = os.getenv("SLACK_BOT_TOKEN")
    
    if not slack_token:
        logger.error("No Slack token provided. Set SLACK_BOT_TOKEN environment variable or pass as argument.")
        sys.exit(1)
    
    # Create and run server
    server = SlackMCPServer(slack_token)
    await server.run_stdio()


if __name__ == "__main__":
    asyncio.run(main())
