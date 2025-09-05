"""Tests for data models."""

import pytest
from datetime import datetime
from slack_mcp.models.slack import SlackChannel, SlackMessage, SlackUser, SlackWorkspace
from slack_mcp.models.mcp import MCPResource, MCPTool, MCPToolCall, MCPToolResult


def test_slack_user_model():
    """Test SlackUser model."""
    user = SlackUser(
        id="U1234567890",
        name="testuser",
        real_name="Test User",
        display_name="Test",
        email="test@example.com",
        is_bot=False,
        is_admin=True,
        timezone="America/New_York"
    )
    
    assert user.id == "U1234567890"
    assert user.name == "testuser"
    assert user.real_name == "Test User"
    assert user.is_admin is True
    assert user.is_bot is False


def test_slack_channel_model():
    """Test SlackChannel model."""
    channel = SlackChannel(
        id="C1234567890",
        name="general",
        is_private=False,
        is_archived=False,
        is_general=True,
        topic="General discussion",
        purpose="Company-wide announcements and general discussion",
        member_count=50
    )
    
    assert channel.id == "C1234567890"
    assert channel.name == "general"
    assert channel.is_general is True
    assert channel.member_count == 50


def test_slack_message_model():
    """Test SlackMessage model."""
    message = SlackMessage(
        ts="1234567890.123456",
        channel="C1234567890",
        user="U1234567890",
        text="Hello, world!",
        thread_ts=None,
        reply_count=0
    )
    
    assert message.ts == "1234567890.123456"
    assert message.channel == "C1234567890"
    assert message.text == "Hello, world!"
    assert message.reply_count == 0


def test_mcp_resource_model():
    """Test MCPResource model."""
    resource = MCPResource(
        uri="slack://channels",
        name="Slack Channels",
        description="List of all accessible Slack channels",
        mime_type="application/json"
    )
    
    assert resource.uri == "slack://channels"
    assert resource.name == "Slack Channels"
    assert resource.mime_type == "application/json"


def test_mcp_tool_model():
    """Test MCPTool model."""
    tool = MCPTool(
        name="post_message",
        description="Post a message to a Slack channel",
        input_schema={
            "type": "object",
            "properties": {
                "channel": {"type": "string"},
                "text": {"type": "string"}
            },
            "required": ["channel", "text"]
        }
    )
    
    assert tool.name == "post_message"
    assert tool.description == "Post a message to a Slack channel"
    assert "channel" in tool.input_schema["properties"]
