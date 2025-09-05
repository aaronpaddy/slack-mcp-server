"""MCP protocol models."""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class MCPResource(BaseModel):
    """MCP resource model."""
    
    uri: str = Field(..., description="Resource URI")
    name: str = Field(..., description="Resource name")
    description: Optional[str] = Field(default=None, description="Resource description")
    mime_type: Optional[str] = Field(default="text/plain", description="MIME type")


class MCPTool(BaseModel):
    """MCP tool model."""
    
    name: str = Field(..., description="Tool name")
    description: str = Field(..., description="Tool description")
    input_schema: Dict[str, Any] = Field(..., description="JSON schema for tool input")


class MCPToolCall(BaseModel):
    """MCP tool call model."""
    
    name: str = Field(..., description="Tool name")
    arguments: Dict[str, Any] = Field(default_factory=dict, description="Tool arguments")


class MCPToolResult(BaseModel):
    """MCP tool result model."""
    
    content: List[Dict[str, Any]] = Field(..., description="Tool result content")
    is_error: bool = Field(default=False, description="Whether the result is an error")
