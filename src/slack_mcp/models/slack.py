"""Slack data models."""

from datetime import datetime
from typing import List, Optional, Dict, Any, Union
from pydantic import BaseModel, Field


class SlackUser(BaseModel):
    """Slack user model."""
    
    id: str = Field(..., description="User ID")
    name: str = Field(..., description="Username")
    real_name: Optional[str] = Field(default=None, description="Real name")
    display_name: Optional[str] = Field(default=None, description="Display name")
    email: Optional[str] = Field(default=None, description="Email address")
    is_bot: bool = Field(default=False, description="Whether user is a bot")
    is_admin: bool = Field(default=False, description="Whether user is an admin")
    timezone: Optional[str] = Field(default=None, description="User timezone")
    profile_image: Optional[str] = Field(default=None, description="Profile image URL")


class SlackChannel(BaseModel):
    """Slack channel model."""
    
    id: str = Field(..., description="Channel ID")
    name: str = Field(..., description="Channel name")
    is_private: bool = Field(default=False, description="Whether channel is private")
    is_archived: bool = Field(default=False, description="Whether channel is archived")
    is_general: bool = Field(default=False, description="Whether this is the general channel")
    topic: Optional[str] = Field(default=None, description="Channel topic")
    purpose: Optional[str] = Field(default=None, description="Channel purpose")
    member_count: Optional[int] = Field(default=None, description="Number of members")
    created: Optional[datetime] = Field(default=None, description="Channel creation time")


class SlackMessage(BaseModel):
    """Slack message model."""
    
    ts: str = Field(..., description="Message timestamp")
    channel: str = Field(..., description="Channel ID")
    user: Optional[str] = Field(default=None, description="User ID who sent the message")
    text: str = Field(..., description="Message text")
    thread_ts: Optional[str] = Field(default=None, description="Thread timestamp if reply")
    reply_count: Optional[int] = Field(default=0, description="Number of replies")
    reactions: List[Dict[str, Any]] = Field(default_factory=list, description="Message reactions")
    attachments: List[Dict[str, Any]] = Field(default_factory=list, description="Message attachments")
    files: List[Dict[str, Any]] = Field(default_factory=list, description="Attached files")
    edited: Optional[Dict[str, Any]] = Field(default=None, description="Edit information")
    is_starred: bool = Field(default=False, description="Whether message is starred")
    permalink: Optional[str] = Field(default=None, description="Permanent link to message")


class SlackWorkspace(BaseModel):
    """Slack workspace model."""
    
    id: str = Field(..., description="Workspace/team ID")
    name: str = Field(..., description="Workspace name")
    domain: str = Field(..., description="Workspace domain")
    email_domain: Optional[str] = Field(default=None, description="Email domain")
    icon: Optional[Dict[str, Any]] = Field(default=None, description="Workspace icon URLs")
    enterprise_id: Optional[str] = Field(default=None, description="Enterprise ID if applicable")
    enterprise_name: Optional[str] = Field(default=None, description="Enterprise name if applicable")
