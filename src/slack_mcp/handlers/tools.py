"""MCP tool handlers for Slack actions."""

import logging
from typing import List, Dict, Any, Optional
from mcp.types import Tool, TextContent, ImageContent, EmbeddedResource

from ..slack_client import SlackClient, SlackClientError
from ..models.mcp import MCPToolResult

logger = logging.getLogger(__name__)


class ToolHandler:
    """Handles MCP tool operations for Slack actions."""
    
    def __init__(self, slack_client: SlackClient):
        """Initialize with Slack client."""
        self.slack_client = slack_client
    
    def list_tools(self) -> List[Tool]:
        """List all available Slack tools."""
        return [
            Tool(
                name="post_message",
                description="Post a message to a Slack channel",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "channel": {
                            "type": "string",
                            "description": "Channel ID or name (e.g., #general, C1234567890)"
                        },
                        "text": {
                            "type": "string",
                            "description": "Message text to post"
                        },
                        "thread_ts": {
                            "type": "string",
                            "description": "Optional: Reply to a thread by providing the parent message timestamp",
                            "optional": True
                        }
                    },
                    "required": ["channel", "text"]
                }
            ),
            Tool(
                name="get_channel_history",
                description="Get message history from a Slack channel",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "channel": {
                            "type": "string",
                            "description": "Channel ID or name (e.g., #general, C1234567890)"
                        },
                        "limit": {
                            "type": "integer",
                            "description": "Number of messages to retrieve (default: 50, max: 1000)",
                            "minimum": 1,
                            "maximum": 1000,
                            "default": 50
                        },
                        "oldest": {
                            "type": "string",
                            "description": "Optional: Only messages after this timestamp",
                            "optional": True
                        },
                        "latest": {
                            "type": "string", 
                            "description": "Optional: Only messages before this timestamp",
                            "optional": True
                        }
                    },
                    "required": ["channel"]
                }
            ),
            Tool(
                name="list_channels",
                description="List all accessible Slack channels",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "exclude_archived": {
                            "type": "boolean",
                            "description": "Whether to exclude archived channels (default: true)",
                            "default": True
                        },
                        "limit": {
                            "type": "integer",
                            "description": "Maximum number of channels to return (default: 100)",
                            "minimum": 1,
                            "maximum": 1000,
                            "default": 100
                        }
                    },
                    "required": []
                }
            ),
            Tool(
                name="get_user_info",
                description="Get information about a Slack user",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "user_id": {
                            "type": "string",
                            "description": "User ID (e.g., U1234567890)"
                        }
                    },
                    "required": ["user_id"]
                }
            ),
            Tool(
                name="list_users",
                description="List all users in the Slack workspace",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "limit": {
                            "type": "integer",
                            "description": "Maximum number of users to return (default: 100)",
                            "minimum": 1,
                            "maximum": 1000,
                            "default": 100
                        }
                    },
                    "required": []
                }
            ),
            Tool(
                name="search_messages",
                description="Search for messages in Slack (requires search scope)",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "Search query (supports Slack search syntax)"
                        },
                        "count": {
                            "type": "integer",
                            "description": "Number of results to return (default: 20, max: 100)",
                            "minimum": 1,
                            "maximum": 100,
                            "default": 20
                        }
                    },
                    "required": ["query"]
                }
            )
        ]
    
    async def call_tool(self, name: str, arguments: Dict[str, Any]) -> MCPToolResult:
        """Execute a Slack tool."""
        try:
            if name == "post_message":
                return await self._post_message(arguments)
            elif name == "get_channel_history":
                return await self._get_channel_history(arguments)
            elif name == "list_channels":
                return await self._list_channels(arguments)
            elif name == "get_user_info":
                return await self._get_user_info(arguments)
            elif name == "list_users":
                return await self._list_users(arguments)
            elif name == "search_messages":
                return await self._search_messages(arguments)
            else:
                return MCPToolResult(
                    content=[{
                        "type": "text",
                        "text": f"Unknown tool: {name}"
                    }],
                    is_error=True
                )
                
        except SlackClientError as e:
            logger.error(f"Slack API error in tool {name}: {e}")
            return MCPToolResult(
                content=[{
                    "type": "text", 
                    "text": f"Slack API error: {e}"
                }],
                is_error=True
            )
        except Exception as e:
            logger.error(f"Unexpected error in tool {name}: {e}")
            return MCPToolResult(
                content=[{
                    "type": "text",
                    "text": f"Unexpected error: {e}"
                }],
                is_error=True
            )
    
    async def _post_message(self, arguments: Dict[str, Any]) -> MCPToolResult:
        """Post a message to Slack."""
        channel = arguments["channel"]
        text = arguments["text"]
        thread_ts = arguments.get("thread_ts")
        
        # Handle channel name to ID conversion if needed
        if channel.startswith("#"):
            # Find channel by name
            channels = await self.slack_client.list_channels()
            channel_obj = next((c for c in channels if c.name == channel[1:]), None)
            if channel_obj:
                channel = channel_obj.id
            else:
                return MCPToolResult(
                    content=[{
                        "type": "text",
                        "text": f"Channel {channel} not found"
                    }],
                    is_error=True
                )
        
        message = await self.slack_client.post_message(
            channel=channel,
            text=text,
            thread_ts=thread_ts
        )
        
        return MCPToolResult(
            content=[{
                "type": "text",
                "text": f"Message posted successfully to channel {channel}\\nTimestamp: {message.ts}\\nText: {message.text}"
            }]
        )
    
    async def _get_channel_history(self, arguments: Dict[str, Any]) -> MCPToolResult:
        """Get channel message history."""
        channel = arguments["channel"]
        limit = arguments.get("limit", 50)
        oldest = arguments.get("oldest")
        latest = arguments.get("latest")
        
        # Handle channel name to ID conversion if needed
        if channel.startswith("#"):
            channels = await self.slack_client.list_channels()
            channel_obj = next((c for c in channels if c.name == channel[1:]), None)
            if channel_obj:
                channel = channel_obj.id
            else:
                return MCPToolResult(
                    content=[{
                        "type": "text",
                        "text": f"Channel {channel} not found"
                    }],
                    is_error=True
                )
        
        messages = await self.slack_client.get_channel_history(
            channel_id=channel,
            limit=limit,
            oldest=oldest,
            latest=latest
        )
        
        # Format messages for display
        formatted_messages = []
        for msg in messages:
            user_info = ""
            if msg.user:
                try:
                    user = await self.slack_client.get_user_info(msg.user)
                    user_info = f" ({user.display_name or user.real_name or user.name})"
                except:
                    user_info = f" ({msg.user})"
            
            formatted_msg = f"[{msg.ts}]{user_info}: {msg.text}"
            if msg.thread_ts:
                formatted_msg += f" (reply to {msg.thread_ts})"
            formatted_messages.append(formatted_msg)
        
        result_text = f"Retrieved {len(messages)} messages from channel {channel}:\\n\\n"
        result_text += "\\n".join(formatted_messages)
        
        return MCPToolResult(
            content=[{
                "type": "text",
                "text": result_text
            }]
        )
    
    async def _list_channels(self, arguments: Dict[str, Any]) -> MCPToolResult:
        """List Slack channels."""
        exclude_archived = arguments.get("exclude_archived", True)
        limit = arguments.get("limit", 100)
        
        channels = await self.slack_client.list_channels(
            limit=limit,
            exclude_archived=exclude_archived
        )
        
        # Format channels for display
        channel_list = []
        for channel in channels:
            privacy = "private" if channel.is_private else "public"
            archived = " (archived)" if channel.is_archived else ""
            topic = f" - {channel.topic}" if channel.topic else ""
            
            channel_info = f"#{channel.name} ({privacy}){archived}{topic}"
            channel_list.append(channel_info)
        
        result_text = f"Found {len(channels)} channels:\\n\\n"
        result_text += "\\n".join(channel_list)
        
        return MCPToolResult(
            content=[{
                "type": "text",
                "text": result_text
            }]
        )
    
    async def _get_user_info(self, arguments: Dict[str, Any]) -> MCPToolResult:
        """Get user information."""
        user_id = arguments["user_id"]
        
        user = await self.slack_client.get_user_info(user_id)
        
        user_info = f"User Information:\\n"
        user_info += f"ID: {user.id}\\n"
        user_info += f"Username: {user.name}\\n"
        user_info += f"Real Name: {user.real_name or 'N/A'}\\n"
        user_info += f"Display Name: {user.display_name or 'N/A'}\\n"
        user_info += f"Email: {user.email or 'N/A'}\\n"
        user_info += f"Is Bot: {user.is_bot}\\n"
        user_info += f"Is Admin: {user.is_admin}\\n"
        user_info += f"Timezone: {user.timezone or 'N/A'}"
        
        return MCPToolResult(
            content=[{
                "type": "text",
                "text": user_info
            }]
        )
    
    async def _list_users(self, arguments: Dict[str, Any]) -> MCPToolResult:
        """List workspace users."""
        limit = arguments.get("limit", 100)
        
        users = await self.slack_client.list_users(limit=limit)
        
        # Format users for display
        user_list = []
        for user in users:
            bot_indicator = " (bot)" if user.is_bot else ""
            admin_indicator = " (admin)" if user.is_admin else ""
            display_name = user.display_name or user.real_name or user.name
            
            user_info = f"{display_name} (@{user.name}){bot_indicator}{admin_indicator}"
            user_list.append(user_info)
        
        result_text = f"Found {len(users)} users:\\n\\n"
        result_text += "\\n".join(user_list)
        
        return MCPToolResult(
            content=[{
                "type": "text",
                "text": result_text
            }]
        )
    
    async def _search_messages(self, arguments: Dict[str, Any]) -> MCPToolResult:
        """Search messages (placeholder - requires search API scope)."""
        query = arguments["query"]
        count = arguments.get("count", 20)
        
        # Note: This would require the search:read scope and search.messages API
        # For now, return a placeholder message
        return MCPToolResult(
            content=[{
                "type": "text",
                "text": f"Message search is not yet implemented. Would search for: '{query}' (limit: {count})"
            }]
        )
