"""Web server wrapper for Cloud Run deployment."""

import os
import asyncio
from fastapi import FastAPI
from fastapi.responses import JSONResponse
import uvicorn

from .config import get_settings
from .slack_client import SlackClient, SlackClientError

app = FastAPI(title="Slack MCP Server", description="Model Context Protocol server for Slack integration")

@app.get("/")
async def root():
    """Root endpoint - shows server status."""
    return {
        "service": "Slack MCP Server",
        "version": "0.1.0",
        "status": "running",
        "endpoints": {
            "health": "/health",
            "oauth": "/auth/slack/callback",
            "docs": "/docs"
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint for Cloud Run."""
    try:
        # Test if we can create a client (basic validation)
        token = os.getenv("SLACK_BOT_TOKEN")
        if token:
            client = SlackClient(token)
            # Don't actually call Slack API in health check (too slow)
            return {"status": "healthy", "slack_configured": True}
        else:
            return {"status": "healthy", "slack_configured": False}
    except Exception as e:
        return JSONResponse(
            status_code=503,
            content={"status": "unhealthy", "error": str(e)}
        )

@app.get("/auth/slack/callback")
async def oauth_callback():
    """OAuth callback endpoint (placeholder for future OAuth flow)."""
    return {
        "message": "OAuth callback endpoint",
        "status": "This would handle Slack OAuth flow in a full web deployment"
    }

@app.get("/slack/info")
async def slack_info():
    """Get Slack workspace information."""
    try:
        token = os.getenv("SLACK_BOT_TOKEN")
        if not token:
            return JSONResponse(
                status_code=400,
                content={"error": "SLACK_BOT_TOKEN not configured"}
            )
        
        client = SlackClient(token)
        workspace_info = await client.get_workspace_info()
        return {
            "workspace": workspace_info,
            "token_configured": True,
            "status": "connected"
        }
    except SlackClientError as e:
        return JSONResponse(
            status_code=400,
            content={"error": f"Slack API error: {e}"}
        )
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": f"Server error: {e}"}
        )

@app.get("/mcp/info")
async def mcp_info():
    """Information about MCP capabilities."""
    return {
        "protocol": "Model Context Protocol",
        "version": "1.0",
        "capabilities": {
            "resources": [
                "slack://channels",
                "slack://users", 
                "slack://workspace"
            ],
            "tools": [
                "post_message",
                "list_channels",
                "get_channel_history",
                "list_users",
                "get_user_info"
            ]
        }
    }

def main():
    """Run the web server."""
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)

if __name__ == "__main__":
    main()
