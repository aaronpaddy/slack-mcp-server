#!/usr/bin/env python3
"""
Simple MCP connection test.
"""

import asyncio
import os
import sys

async def test_mcp_connection():
    """Test basic MCP connection."""
    
    # Check token
    token = os.getenv("SLACK_BOT_TOKEN")
    if not token:
        print("❌ SLACK_BOT_TOKEN not set")
        return False
    
    print(f"✅ Token found: {token[:15]}...")
    
    try:
        from mcp import ClientSession, StdioServerParameters
        from mcp.client.stdio import stdio_client
        
        print("✅ MCP imports successful")
        
        # Create server parameters
        server_params = StdioServerParameters(
            command="slack-mcp-server",
            args=["--token", token, "--log-level", "ERROR"]  # Reduce noise
        )
        
        print("🔧 Connecting to MCP server...")
        
        # Test connection with timeout
        try:
            async with asyncio.timeout(15):  # 15 second timeout
                async with stdio_client(server_params) as (read, write):
                    print("✅ stdio_client connected")
                    
                    async with ClientSession(read, write) as session:
                        print("✅ ClientSession created")
                        
                        # Initialize
                        await session.initialize()
                        print("✅ Session initialized!")
                        
                        # Test list resources
                        resources = await session.list_resources()
                        print(f"✅ Found {len(resources.resources)} resources:")
                        for r in resources.resources[:3]:  # Show first 3
                            print(f"   - {r.name}")
                        
                        # Test list tools  
                        tools = await session.list_tools()
                        print(f"✅ Found {len(tools.tools)} tools:")
                        for t in tools.tools[:3]:  # Show first 3
                            print(f"   - {t.name}")
                        
                        print("🎉 MCP connection test successful!")
                        return True
                        
        except asyncio.TimeoutError:
            print("❌ Connection timed out - server may be slow to start")
            return False
            
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        print(f"Error type: {type(e).__name__}")
        
        # Show more details
        import traceback
        print("\nFull traceback:")
        traceback.print_exc()
        return False

def main():
    """Run the test."""
    print("🧪 Simple MCP Connection Test")
    print("=" * 30)
    
    success = asyncio.run(test_mcp_connection())
    
    print("\n" + "=" * 30)
    if success:
        print("🎉 Test successful! Your setup is working.")
        print("\nNow try: python examples/basic_usage.py")
    else:
        print("❌ Test failed. Check the errors above.")

if __name__ == "__main__":
    main()
