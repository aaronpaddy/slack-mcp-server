"""Configuration management for Slack MCP Server."""

from typing import Optional
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )
    
    # Slack OAuth Configuration
    slack_client_id: Optional[str] = Field(default=None, description="Slack OAuth client ID")
    slack_client_secret: Optional[str] = Field(default=None, description="Slack OAuth client secret")
    slack_signing_secret: Optional[str] = Field(default=None, description="Slack signing secret for request verification")
    
    # Server Configuration
    host: str = Field(default="0.0.0.0", description="Server host")
    port: int = Field(default=8000, description="Server port")
    debug: bool = Field(default=False, description="Debug mode")
    log_level: str = Field(default="INFO", description="Logging level")
    
    # MCP Configuration
    mcp_server_name: str = Field(default="slack-mcp-server", description="MCP server name")
    mcp_server_version: str = Field(default="0.1.0", description="MCP server version")
    
    # Security
    secret_key: Optional[str] = Field(default=None, description="Secret key for JWT tokens and encryption")
    
    # Optional: Database
    database_url: Optional[str] = Field(default=None, description="Database URL for persistent storage")
    
    # Optional: Redis
    redis_url: Optional[str] = Field(default=None, description="Redis URL for caching")
    
    @property
    def slack_oauth_redirect_uri(self) -> str:
        """Generate the OAuth redirect URI."""
        return f"http://{self.host}:{self.port}/auth/slack/callback"
    
    def validate_oauth_settings(self) -> None:
        """Validate that required OAuth settings are present."""
        if not self.slack_client_id:
            raise ValueError("SLACK_CLIENT_ID is required")
        if not self.slack_client_secret:
            raise ValueError("SLACK_CLIENT_SECRET is required")
        if not self.slack_signing_secret:
            raise ValueError("SLACK_SIGNING_SECRET is required")
        if not self.secret_key:
            raise ValueError("SECRET_KEY is required")


# Global settings instance - will be initialized when needed
settings: Optional[Settings] = None


def get_settings() -> Settings:
    """Get or create the global settings instance."""
    global settings
    if settings is None:
        settings = Settings()
    return settings
