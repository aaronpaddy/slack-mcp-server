"""Tests for configuration management."""

import pytest
from unittest.mock import patch
from slack_mcp.config import Settings


def test_settings_defaults():
    """Test default settings values."""
    with patch.dict('os.environ', {
        'SLACK_CLIENT_ID': 'test_client_id',
        'SLACK_CLIENT_SECRET': 'test_client_secret', 
        'SLACK_SIGNING_SECRET': 'test_signing_secret',
        'SECRET_KEY': 'test_secret_key'
    }):
        settings = Settings()
        
        assert settings.slack_client_id == 'test_client_id'
        assert settings.slack_client_secret == 'test_client_secret'
        assert settings.slack_signing_secret == 'test_signing_secret'
        assert settings.secret_key == 'test_secret_key'
        
        assert settings.host == '0.0.0.0'
        assert settings.port == 8000
        assert settings.debug is False
        assert settings.log_level == 'INFO'
        assert settings.mcp_server_name == 'slack-mcp-server'
        assert settings.mcp_server_version == '0.1.0'


def test_oauth_redirect_uri():
    """Test OAuth redirect URI generation."""
    with patch.dict('os.environ', {
        'SLACK_CLIENT_ID': 'test_client_id',
        'SLACK_CLIENT_SECRET': 'test_client_secret',
        'SLACK_SIGNING_SECRET': 'test_signing_secret', 
        'SECRET_KEY': 'test_secret_key'
    }):
        settings = Settings()
        expected_uri = f"http://{settings.host}:{settings.port}/auth/slack/callback"
        assert settings.slack_oauth_redirect_uri == expected_uri
