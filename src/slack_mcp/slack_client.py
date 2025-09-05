"""Slack API client wrapper."""

import logging
from typing import List, Optional, Dict, Any
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

from .models.slack import SlackChannel, SlackMessage, SlackUser, SlackWorkspace
from .config import settings

logger = logging.getLogger(__name__)


class SlackClientError(Exception):
    """Custom exception for Slack client errors."""
    pass


class SlackClient:
    """Wrapper around Slack SDK WebClient with error handling and data models."""
    
    def __init__(self, token: str):
        """Initialize Slack client with OAuth token."""
        self.client = WebClient(token=token)
        self.token = token
        
    async def test_auth(self) -> Dict[str, Any]:
        """Test the authentication token."""
        try:
            response = self.client.auth_test()
            return response.data
        except SlackApiError as e:
            logger.error(f"Auth test failed: {e.response['error']}")
            raise SlackClientError(f"Authentication failed: {e.response['error']}")
    
    async def get_workspace_info(self) -> SlackWorkspace:
        """Get workspace information."""
        try:
            response = self.client.team_info()
            team_data = response.data["team"]
            
            return SlackWorkspace(
                id=team_data["id"],
                name=team_data["name"],
                domain=team_data["domain"],
                email_domain=team_data.get("email_domain"),
                icon=team_data.get("icon"),
                enterprise_id=team_data.get("enterprise_id"),
                enterprise_name=team_data.get("enterprise_name")
            )
        except SlackApiError as e:
            logger.error(f"Failed to get workspace info: {e.response['error']}")
            raise SlackClientError(f"Failed to get workspace info: {e.response['error']}")
    
    async def list_channels(self, limit: int = 100, exclude_archived: bool = True) -> List[SlackChannel]:
        """List all channels the bot has access to."""
        try:
            channels = []
            cursor = None
            
            while True:
                response = self.client.conversations_list(
                    limit=limit,
                    cursor=cursor,
                    exclude_archived=exclude_archived,
                    types="public_channel,private_channel"
                )
                
                for channel_data in response.data["channels"]:
                    channel = SlackChannel(
                        id=channel_data["id"],
                        name=channel_data["name"],
                        is_private=channel_data["is_private"],
                        is_archived=channel_data.get("is_archived", False),
                        is_general=channel_data.get("is_general", False),
                        topic=channel_data.get("topic", {}).get("value"),
                        purpose=channel_data.get("purpose", {}).get("value"),
                        member_count=channel_data.get("num_members")
                    )
                    channels.append(channel)
                
                cursor = response.data.get("response_metadata", {}).get("next_cursor")
                if not cursor:
                    break
            
            return channels
            
        except SlackApiError as e:
            logger.error(f"Failed to list channels: {e.response['error']}")
            raise SlackClientError(f"Failed to list channels: {e.response['error']}")
    
    async def get_channel_history(
        self, 
        channel_id: str, 
        limit: int = 100,
        oldest: Optional[str] = None,
        latest: Optional[str] = None
    ) -> List[SlackMessage]:
        """Get message history from a channel."""
        try:
            response = self.client.conversations_history(
                channel=channel_id,
                limit=limit,
                oldest=oldest,
                latest=latest
            )
            
            messages = []
            for msg_data in response.data["messages"]:
                message = SlackMessage(
                    ts=msg_data["ts"],
                    channel=channel_id,
                    user=msg_data.get("user"),
                    text=msg_data.get("text", ""),
                    thread_ts=msg_data.get("thread_ts"),
                    reply_count=msg_data.get("reply_count", 0),
                    reactions=msg_data.get("reactions", []),
                    attachments=msg_data.get("attachments", []),
                    files=msg_data.get("files", []),
                    edited=msg_data.get("edited"),
                    permalink=msg_data.get("permalink")
                )
                messages.append(message)
            
            return messages
            
        except SlackApiError as e:
            logger.error(f"Failed to get channel history: {e.response['error']}")
            raise SlackClientError(f"Failed to get channel history: {e.response['error']}")
    
    async def post_message(
        self, 
        channel: str, 
        text: str,
        thread_ts: Optional[str] = None,
        attachments: Optional[List[Dict[str, Any]]] = None
    ) -> SlackMessage:
        """Post a message to a channel."""
        try:
            response = self.client.chat_postMessage(
                channel=channel,
                text=text,
                thread_ts=thread_ts,
                attachments=attachments
            )
            
            msg_data = response.data["message"]
            return SlackMessage(
                ts=msg_data["ts"],
                channel=channel,
                user=msg_data.get("user"),
                text=msg_data.get("text", ""),
                thread_ts=msg_data.get("thread_ts"),
                attachments=msg_data.get("attachments", [])
            )
            
        except SlackApiError as e:
            logger.error(f"Failed to post message: {e.response['error']}")
            raise SlackClientError(f"Failed to post message: {e.response['error']}")
    
    async def get_user_info(self, user_id: str) -> SlackUser:
        """Get information about a user."""
        try:
            response = self.client.users_info(user=user_id)
            user_data = response.data["user"]
            
            return SlackUser(
                id=user_data["id"],
                name=user_data["name"],
                real_name=user_data.get("real_name"),
                display_name=user_data.get("profile", {}).get("display_name"),
                email=user_data.get("profile", {}).get("email"),
                is_bot=user_data.get("is_bot", False),
                is_admin=user_data.get("is_admin", False),
                timezone=user_data.get("tz"),
                profile_image=user_data.get("profile", {}).get("image_72")
            )
            
        except SlackApiError as e:
            logger.error(f"Failed to get user info: {e.response['error']}")
            raise SlackClientError(f"Failed to get user info: {e.response['error']}")
    
    async def list_users(self, limit: int = 100) -> List[SlackUser]:
        """List all users in the workspace."""
        try:
            users = []
            cursor = None
            
            while True:
                response = self.client.users_list(
                    limit=limit,
                    cursor=cursor
                )
                
                for user_data in response.data["members"]:
                    if user_data.get("deleted"):
                        continue
                        
                    user = SlackUser(
                        id=user_data["id"],
                        name=user_data["name"],
                        real_name=user_data.get("real_name"),
                        display_name=user_data.get("profile", {}).get("display_name"),
                        email=user_data.get("profile", {}).get("email"),
                        is_bot=user_data.get("is_bot", False),
                        is_admin=user_data.get("is_admin", False),
                        timezone=user_data.get("tz"),
                        profile_image=user_data.get("profile", {}).get("image_72")
                    )
                    users.append(user)
                
                cursor = response.data.get("response_metadata", {}).get("next_cursor")
                if not cursor:
                    break
            
            return users
            
        except SlackApiError as e:
            logger.error(f"Failed to list users: {e.response['error']}")
            raise SlackClientError(f"Failed to list users: {e.response['error']}")
