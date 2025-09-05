"""OAuth flow implementation for Slack."""

import asyncio
import logging
import secrets
import webbrowser
from typing import Optional
from urllib.parse import urlencode
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse
import uvicorn
import httpx

from .config import get_settings

logger = logging.getLogger(__name__)


class OAuthFlow:
    """Handles Slack OAuth 2.0 flow."""
    
    def __init__(self):
        self.app = FastAPI(title="Slack MCP OAuth")
        self.state = secrets.token_urlsafe(32)
        self.token: Optional[str] = None
        self.server_task: Optional[asyncio.Task] = None
        self.setup_routes()
    
    def setup_routes(self):
        """Setup FastAPI routes for OAuth flow."""
        
        @self.app.get("/")
        async def root():
            """Root endpoint with OAuth link."""
            auth_url = self.get_authorization_url()
            
            html_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <title>Slack MCP Server OAuth</title>
                <style>
                    body {{ font-family: Arial, sans-serif; margin: 40px; }}
                    .container {{ max-width: 600px; margin: 0 auto; }}
                    .button {{ 
                        display: inline-block; 
                        padding: 12px 24px; 
                        background-color: #4A154B; 
                        color: white; 
                        text-decoration: none; 
                        border-radius: 4px; 
                        font-weight: bold;
                    }}
                    .button:hover {{ background-color: #611f69; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <h1>Slack MCP Server OAuth</h1>
                    <p>Click the button below to authorize this application with your Slack workspace:</p>
                    <p><a href="{auth_url}" class="button">Add to Slack</a></p>
                    <p><small>This will redirect you to Slack to authorize the application.</small></p>
                </div>
            </body>
            </html>
            """
            return HTMLResponse(content=html_content)
        
        @self.app.get("/auth/slack/callback")
        async def oauth_callback(request: Request):
            """Handle OAuth callback from Slack."""
            code = request.query_params.get("code")
            state = request.query_params.get("state")
            error = request.query_params.get("error")
            
            if error:
                logger.error(f"OAuth error: {error}")
                return HTMLResponse(
                    content=f"<h1>OAuth Error</h1><p>Error: {error}</p>",
                    status_code=400
                )
            
            if not code:
                logger.error("No authorization code received")
                return HTMLResponse(
                    content="<h1>OAuth Error</h1><p>No authorization code received</p>",
                    status_code=400
                )
            
            if state != self.state:
                logger.error("Invalid state parameter")
                return HTMLResponse(
                    content="<h1>OAuth Error</h1><p>Invalid state parameter</p>",
                    status_code=400
                )
            
            # Exchange code for token
            try:
                token = await self.exchange_code_for_token(code)
                if token:
                    self.token = token
                    return HTMLResponse(
                        content="""
                        <h1>Success!</h1>
                        <p>Authorization successful. You can now close this window and return to your terminal.</p>
                        <script>setTimeout(() => window.close(), 3000);</script>
                        """
                    )
                else:
                    return HTMLResponse(
                        content="<h1>OAuth Error</h1><p>Failed to exchange code for token</p>",
                        status_code=500
                    )
            except Exception as e:
                logger.error(f"Token exchange error: {e}")
                return HTMLResponse(
                    content=f"<h1>OAuth Error</h1><p>Token exchange failed: {e}</p>",
                    status_code=500
                )
    
    def get_authorization_url(self) -> str:
        """Generate Slack OAuth authorization URL."""
        settings = get_settings()
        settings.validate_oauth_settings()
        
        params = {
            "client_id": settings.slack_client_id,
            "scope": "channels:read,groups:read,chat:write,users:read,team:read",
            "redirect_uri": settings.slack_oauth_redirect_uri,
            "state": self.state,
            "response_type": "code"
        }
        
        return f"https://slack.com/oauth/v2/authorize?{urlencode(params)}"
    
    async def exchange_code_for_token(self, code: str) -> Optional[str]:
        """Exchange authorization code for access token."""
        settings = get_settings()
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://slack.com/api/oauth.v2.access",
                data={
                    "client_id": settings.slack_client_id,
                    "client_secret": settings.slack_client_secret,
                    "code": code,
                    "redirect_uri": settings.slack_oauth_redirect_uri
                }
            )
            
            if response.status_code != 200:
                logger.error(f"Token exchange failed with status {response.status_code}")
                return None
            
            data = response.json()
            
            if not data.get("ok"):
                logger.error(f"Token exchange failed: {data.get('error')}")
                return None
            
            # Return the bot token
            return data.get("access_token")
    
    async def start_server(self):
        """Start the OAuth server."""
        settings = get_settings()
        
        config = uvicorn.Config(
            self.app,
            host=settings.host,
            port=settings.port,
            log_level="warning"  # Reduce uvicorn logging
        )
        server = uvicorn.Server(config)
        
        # Start server in background
        self.server_task = asyncio.create_task(server.serve())
        
        # Wait a moment for server to start
        await asyncio.sleep(1)
        
        return server
    
    async def stop_server(self):
        """Stop the OAuth server."""
        if self.server_task:
            self.server_task.cancel()
            try:
                await self.server_task
            except asyncio.CancelledError:
                pass


async def run_oauth_flow() -> Optional[str]:
    """Run the complete OAuth flow."""
    oauth = OAuthFlow()
    
    try:
        # Start the server
        server = await oauth.start_server()
        
        # Open browser to OAuth URL
        settings = get_settings()
        oauth_url = f"http://{settings.host}:{settings.port}"
        print(f"\\nStarting OAuth flow...")
        print(f"Opening browser to: {oauth_url}")
        print("If the browser doesn't open automatically, please visit the URL above.")
        
        webbrowser.open(oauth_url)
        
        # Wait for OAuth completion (max 5 minutes)
        for _ in range(300):  # 5 minutes in seconds
            if oauth.token:
                break
            await asyncio.sleep(1)
        
        if oauth.token:
            print("\\nOAuth flow completed successfully!")
            return oauth.token
        else:
            print("\\nOAuth flow timed out or was cancelled.")
            return None
            
    except Exception as e:
        logger.error(f"OAuth flow error: {e}")
        return None
    finally:
        # Clean up server
        await oauth.stop_server()
