#!/usr/bin/env python3
"""
Basic test script for Slack MCP Server.
This script tests core functionality without requiring a real Slack token.
"""

import asyncio
import sys
import os

# Add src to path so we can import our modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from slack_mcp.config import get_settings, Settings
from slack_mcp.models.slack import SlackChannel, SlackUser, SlackMessage
from slack_mcp.models.mcp import MCPResource, MCPTool


def test_configuration():
    """Test configuration loading."""
    print("🔧 Testing Configuration...")
    
    try:
        # Test default settings
        settings = Settings()
        assert settings.host == "0.0.0.0"
        assert settings.port == 8000
        assert settings.mcp_server_name == "slack-mcp-server"
        print("  ✅ Default configuration loaded successfully")
        
        # Test OAuth redirect URI generation
        redirect_uri = settings.slack_oauth_redirect_uri
        expected = f"http://{settings.host}:{settings.port}/auth/slack/callback"
        assert redirect_uri == expected
        print("  ✅ OAuth redirect URI generated correctly")
        
        return True
    except Exception as e:
        print(f"  ❌ Configuration test failed: {e}")
        return False


def test_models():
    """Test data models."""
    print("📊 Testing Data Models...")
    
    try:
        # Test Slack models
        channel = SlackChannel(
            id="C1234567890",
            name="general",
            is_private=False,
            is_archived=False,
            is_general=True
        )
        assert channel.id == "C1234567890"
        assert channel.name == "general"
        print("  ✅ SlackChannel model works")
        
        user = SlackUser(
            id="U1234567890",
            name="testuser",
            is_bot=False
        )
        assert user.id == "U1234567890"
        assert user.name == "testuser"
        print("  ✅ SlackUser model works")
        
        message = SlackMessage(
            ts="1234567890.123456",
            channel="C1234567890",
            text="Hello, world!"
        )
        assert message.ts == "1234567890.123456"
        assert message.text == "Hello, world!"
        print("  ✅ SlackMessage model works")
        
        # Test MCP models
        resource = MCPResource(
            uri="slack://channels",
            name="Slack Channels",
            description="List of channels"
        )
        assert resource.uri == "slack://channels"
        print("  ✅ MCPResource model works")
        
        tool = MCPTool(
            name="post_message",
            description="Post a message",
            input_schema={"type": "object", "properties": {}}
        )
        assert tool.name == "post_message"
        print("  ✅ MCPTool model works")
        
        return True
    except Exception as e:
        print(f"  ❌ Models test failed: {e}")
        return False


def test_imports():
    """Test that all modules can be imported."""
    print("📦 Testing Module Imports...")
    
    try:
        from slack_mcp import SlackMCPServer, get_settings
        print("  ✅ Main modules imported successfully")
        
        from slack_mcp.slack_client import SlackClient
        print("  ✅ SlackClient imported successfully")
        
        from slack_mcp.handlers.resources import ResourceHandler
        from slack_mcp.handlers.tools import ToolHandler
        print("  ✅ Handler modules imported successfully")
        
        from slack_mcp.oauth import OAuthFlow
        print("  ✅ OAuth module imported successfully")
        
        return True
    except Exception as e:
        print(f"  ❌ Import test failed: {e}")
        return False


def test_cli_availability():
    """Test that CLI command is available."""
    print("🖥️  Testing CLI Availability...")
    
    try:
        import subprocess
        result = subprocess.run(
            ["slack-mcp-server", "--version"], 
            capture_output=True, 
            text=True,
            timeout=10
        )
        
        if result.returncode == 0 and "Slack MCP Server" in result.stdout:
            print("  ✅ CLI command works and returns version")
            return True
        else:
            print(f"  ❌ CLI command failed: {result.stderr}")
            return False
    except subprocess.TimeoutExpired:
        print("  ❌ CLI command timed out")
        return False
    except FileNotFoundError:
        print("  ❌ CLI command not found - make sure you've installed with 'pip install -e .'")
        return False
    except Exception as e:
        print(f"  ❌ CLI test failed: {e}")
        return False


async def test_server_creation():
    """Test that we can create a server instance."""
    print("🚀 Testing Server Creation...")
    
    try:
        from slack_mcp.server import SlackMCPServer
        
        # Create server with fake token (won't connect, but should initialize)
        server = SlackMCPServer("xoxb-fake-token-for-testing")
        
        # Check that server has the expected attributes
        assert hasattr(server, 'slack_client')
        assert hasattr(server, 'resource_handler')
        assert hasattr(server, 'tool_handler')
        assert hasattr(server, 'server')
        
        print("  ✅ Server instance created successfully")
        return True
    except Exception as e:
        print(f"  ❌ Server creation test failed: {e}")
        return False


def main():
    """Run all tests."""
    print("🧪 Slack MCP Server - Basic Tests")
    print("=" * 40)
    
    tests = [
        test_imports,
        test_configuration,
        test_models,
        test_cli_availability,
    ]
    
    async_tests = [
        test_server_creation,
    ]
    
    passed = 0
    total = len(tests) + len(async_tests)
    
    # Run synchronous tests
    for test in tests:
        if test():
            passed += 1
        print()
    
    # Run async tests
    for test in async_tests:
        if asyncio.run(test()):
            passed += 1
        print()
    
    print("=" * 40)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! The Slack MCP Server is working correctly.")
        print("\nNext steps:")
        print("1. Set up a Slack app and get your credentials")
        print("2. Run: slack-mcp-server --oauth")
        print("3. Test with a real Slack workspace using: python examples/basic_usage.py")
        return 0
    else:
        print("❌ Some tests failed. Please check the errors above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
