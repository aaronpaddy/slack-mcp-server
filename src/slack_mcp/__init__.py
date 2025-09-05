"""Slack MCP Server - A Model Context Protocol server for Slack integration."""

__version__ = "0.1.0"
__author__ = "Aaron Paddy"
__email__ = "aaron@example.com"

from .server import SlackMCPServer
from .config import Settings, get_settings

__all__ = ["SlackMCPServer", "Settings", "get_settings"]
