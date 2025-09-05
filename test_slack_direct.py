#!/usr/bin/env python3
"""Test Slack functionality directly without MCP."""

import asyncio
import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from slack_mcp.slack_client import SlackClient

async def test_slack_direct():
    """Test Slack client directly."""
    
    token = os.getenv("SLACK_BOT_TOKEN")
    if not token:
        print("❌ SLACK_BOT_TOKEN not set")
        return
    
    print("🔧 Testing Slack client directly...")
    client = SlackClient(token)
    
    try:
        # Test auth
        auth_info = await client.test_auth()
        print(f"✅ Auth successful: {auth_info}")
        
        # Test list channels
        channels = await client.list_channels(limit=5)
        print(f"✅ Found {len(channels)} channels:")
        for channel in channels:
            print(f"   - #{channel.name} (ID: {channel.id})")
        
        # Test list users
        users = await client.list_users(limit=5)
        print(f"✅ Found {len(users)} users:")
        for user in users:
            print(f"   - {user.real_name or user.name} (@{user.name})")
        
        # Test get workspace info
        workspace = await client.get_workspace_info()
        print(f"✅ Workspace: {workspace.name} ({workspace.domain})")
        
        print("\n🎉 All Slack operations work perfectly!")
        print("✅ Your Slack MCP Server backend is fully functional")
        
    except Exception as e:
        print(f"❌ Slack test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_slack_direct())
