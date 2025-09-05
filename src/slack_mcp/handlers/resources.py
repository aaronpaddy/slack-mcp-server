"""MCP resource handlers for Slack data."""

import logging
from typing import List, Optional, Any, Dict
from mcp.types import Resource, TextResourceContents, BlobResourceContents

from ..slack_client import SlackClient, SlackClientError
from ..models.slack import SlackChannel, SlackMessage, SlackUser

logger = logging.getLogger(__name__)


class ResourceHandler:
    """Handles MCP resource operations for Slack data."""
    
    def __init__(self, slack_client: SlackClient):
        """Initialize with Slack client."""
        self.slack_client = slack_client
    
    async def list_resources(self) -> List[Resource]:
        """List all available Slack resources."""
        resources = []
        
        try:
            # Add channels resource
            resources.append(Resource(
                uri="slack://channels",
                name="Slack Channels",
                description="List of all accessible Slack channels",
                mimeType="application/json"
            ))
            
            # Add users resource
            resources.append(Resource(
                uri="slack://users", 
                name="Slack Users",
                description="List of all users in the workspace",
                mimeType="application/json"
            ))
            
            # Add workspace resource
            resources.append(Resource(
                uri="slack://workspace",
                name="Slack Workspace",
                description="Information about the current Slack workspace",
                mimeType="application/json"
            ))
            
            # Get channels to create individual channel resources
            channels = await self.slack_client.list_channels()
            for channel in channels:
                resources.append(Resource(
                    uri=f"slack://channels/{channel.id}",
                    name=f"#{channel.name}",
                    description=f"Messages from #{channel.name} channel",
                    mimeType="application/json"
                ))
                
                # Add channel history resource
                resources.append(Resource(
                    uri=f"slack://channels/{channel.id}/history",
                    name=f"#{channel.name} History",
                    description=f"Message history from #{channel.name} channel",
                    mimeType="application/json"
                ))
            
        except SlackClientError as e:
            logger.error(f"Error listing resources: {e}")
            # Return basic resources even if Slack API fails
            resources = [
                Resource(
                    uri="slack://error",
                    name="Slack API Error",
                    description=f"Error accessing Slack API: {e}",
                    mimeType="text/plain"
                )
            ]
        
        return resources
    
    async def read_resource(self, uri: str) -> str | bytes:
        """Read a specific Slack resource."""
        try:
            if uri == "slack://channels":
                return await self._read_channels()
            elif uri == "slack://users":
                return await self._read_users()
            elif uri == "slack://workspace":
                return await self._read_workspace()
            elif uri.startswith("slack://channels/") and uri.endswith("/history"):
                # Extract channel ID from URI like slack://channels/C1234567890/history
                channel_id = uri.split("/")[3]
                return await self._read_channel_history(channel_id)
            elif uri.startswith("slack://channels/"):
                # Extract channel ID from URI like slack://channels/C1234567890
                channel_id = uri.split("/")[3]
                return await self._read_channel_info(channel_id)
            else:
                raise ValueError(f"Unknown resource URI: {uri}")
                
        except SlackClientError as e:
            logger.error(f"Error reading resource {uri}: {e}")
            return f"Error reading resource: {e}"
        except Exception as e:
            logger.error(f"Unexpected error reading resource {uri}: {e}")
            return f"Unexpected error: {e}"
    
    async def _read_channels(self) -> str:
        """Read all channels."""
        channels = await self.slack_client.list_channels()
        
        # Convert to JSON-serializable format
        channels_data = []
        for channel in channels:
            channels_data.append({
                "id": channel.id,
                "name": channel.name,
                "is_private": channel.is_private,
                "is_archived": channel.is_archived,
                "is_general": channel.is_general,
                "topic": channel.topic,
                "purpose": channel.purpose,
                "member_count": channel.member_count
            })
        
        import json
        return json.dumps(channels_data, indent=2)
    
    async def _read_users(self) -> str:
        """Read all users."""
        users = await self.slack_client.list_users()
        
        # Convert to JSON-serializable format
        users_data = []
        for user in users:
            users_data.append({
                "id": user.id,
                "name": user.name,
                "real_name": user.real_name,
                "display_name": user.display_name,
                "email": user.email,
                "is_bot": user.is_bot,
                "is_admin": user.is_admin,
                "timezone": user.timezone
            })
        
        import json
        return json.dumps(users_data, indent=2)
    
    async def _read_workspace(self) -> str:
        """Read workspace information."""
        workspace = await self.slack_client.get_workspace_info()
        
        workspace_data = {
            "id": workspace.id,
            "name": workspace.name,
            "domain": workspace.domain,
            "email_domain": workspace.email_domain,
            "enterprise_id": workspace.enterprise_id,
            "enterprise_name": workspace.enterprise_name
        }
        
        import json
        return json.dumps(workspace_data, indent=2)
    
    async def _read_channel_info(self, channel_id: str) -> str:
        """Read information about a specific channel."""
        channels = await self.slack_client.list_channels()
        channel = next((c for c in channels if c.id == channel_id), None)
        
        if not channel:
            raise ValueError(f"Channel {channel_id} not found")
        
        channel_data = {
            "id": channel.id,
            "name": channel.name,
            "is_private": channel.is_private,
            "is_archived": channel.is_archived,
            "is_general": channel.is_general,
            "topic": channel.topic,
            "purpose": channel.purpose,
            "member_count": channel.member_count
        }
        
        import json
        return json.dumps(channel_data, indent=2)
    
    async def _read_channel_history(self, channel_id: str, limit: int = 50) -> str:
        """Read message history from a specific channel."""
        messages = await self.slack_client.get_channel_history(channel_id, limit=limit)
        
        # Convert to JSON-serializable format
        messages_data = []
        for message in messages:
            messages_data.append({
                "timestamp": message.ts,
                "channel": message.channel,
                "user": message.user,
                "text": message.text,
                "thread_ts": message.thread_ts,
                "reply_count": message.reply_count,
                "reactions": message.reactions,
                "attachments": message.attachments,
                "files": message.files,
                "edited": message.edited,
                "permalink": message.permalink
            })
        
        import json
        return json.dumps(messages_data, indent=2)
