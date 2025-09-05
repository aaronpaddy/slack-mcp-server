#!/usr/bin/env python3
"""Debug script to check what our server is returning."""

import asyncio
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from slack_mcp.server import SlackMCPServer
from mcp.types import ListResourcesResult, Resource

async def test_server_response():
    """Test what our server returns directly."""
    
    token = os.getenv("SLACK_BOT_TOKEN")
    if not token:
        print("❌ SLACK_BOT_TOKEN not set")
        return
    
    print("🔧 Creating server...")
    server = SlackMCPServer(token)
    
    print("🔧 Testing resource handler directly...")
    try:
        resources = await server.resource_handler.list_resources()
        print(f"✅ Resource handler returned {len(resources)} resources")
        print(f"First resource type: {type(resources[0])}")
        print(f"First resource: {resources[0]}")
        
        # Test creating ListResourcesResult directly
        result = ListResourcesResult(resources=resources, nextCursor=None)
        print(f"✅ ListResourcesResult created: {type(result)}")
        print(f"Result dict: {result.model_dump()}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_server_response())
