#!/usr/bin/env python3
"""
Basic usage example for Slack MCP Server.

This example demonstrates how to connect to the Slack MCP server
and perform basic operations like listing channels and posting messages.
"""

import asyncio
import os
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


async def main():
    """Main example function."""
    
    # Get Slack token from environment
    slack_token = os.getenv("SLACK_BOT_TOKEN")
    if not slack_token:
        print("Error: SLACK_BOT_TOKEN environment variable is required")
        print("Set it with: export SLACK_BOT_TOKEN=your_bot_token_here")
        return
    
    # Set up server parameters
    server_params = StdioServerParameters(
        command="slack-mcp-server",
        args=["--token", slack_token, "--log-level", "WARNING"]
    )
    
    print("🚀 Connecting to Slack MCP Server...")
    
    try:
        # Connect to the server
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                # Initialize the connection
                await session.initialize()
                print("✅ Connected successfully!")
                
                # List available resources
                print("\\n📋 Available Resources:")
                resources = await session.list_resources()
                for resource in resources.resources:
                    print(f"  - {resource.name}: {resource.uri}")
                
                # List available tools
                print("\\n🛠️  Available Tools:")
                tools = await session.list_tools()
                for tool in tools.tools:
                    print(f"  - {tool.name}: {tool.description}")
                
                # Read channels resource
                print("\\n📺 Reading Slack Channels:")
                try:
                    channels_result = await session.read_resource("slack://channels")
                    print("Channels data retrieved successfully!")
                    # Print first few lines of the JSON
                    content = channels_result.contents[0].text
                    lines = content.split('\\n')[:10]
                    for line in lines:
                        print(f"  {line}")
                    if len(content.split('\\n')) > 10:
                        print("  ...")
                except Exception as e:
                    print(f"Error reading channels: {e}")
                
                # Try to list channels using the tool
                print("\\n🔧 Using list_channels tool:")
                try:
                    result = await session.call_tool("list_channels", {"limit": 5})
                    if result.isError:
                        print(f"Error: {result.content[0].text}")
                    else:
                        print("Channels listed successfully!")
                        print(result.content[0].text[:500] + "..." if len(result.content[0].text) > 500 else result.content[0].text)
                except Exception as e:
                    print(f"Error calling list_channels tool: {e}")
                
                print("\\n✨ Example completed successfully!")
                
    except Exception as e:
        print(f"❌ Error connecting to server: {e}")
        print("\\nTroubleshooting:")
        print("1. Make sure slack-mcp-server is installed: pip install -e .")
        print("2. Verify your SLACK_BOT_TOKEN is valid")
        print("3. Check that your Slack app has the required permissions")


if __name__ == "__main__":
    asyncio.run(main())
