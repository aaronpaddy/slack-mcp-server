# 🚀 Quick Start Guide

Get up and running with Slack MCP Server in 5 minutes!

## Prerequisites

- Python 3.11 or higher
- A Slack workspace where you can install apps

## 1. Setup

```bash
# Clone the repository
git clone https://github.com/aaronpaddy/slack-mcp-server.git
cd slack-mcp-server

# Run the setup script
./scripts/setup.sh
```

## 2. Create Slack App

1. Go to [Slack API](https://api.slack.com/apps) and click "Create New App"
2. Choose "From scratch"
3. Give your app a name (e.g., "MCP Bot") and select your workspace
4. Go to "OAuth & Permissions" and add these scopes:
   - `channels:read` - View basic information about public channels
   - `groups:read` - View basic information about private channels  
   - `chat:write` - Send messages as the app
   - `users:read` - View people in the workspace
   - `team:read` - View workspace information

5. Set the redirect URL to: `http://localhost:8000/auth/slack/callback`
6. Note down your:
   - Client ID (from "Basic Information")
   - Client Secret (from "Basic Information")
   - Signing Secret (from "Basic Information")

## 3. Configure Environment

```bash
# Copy the example environment file
cp .env.example .env

# Edit .env with your Slack app credentials
# SLACK_CLIENT_ID=your_client_id_here
# SLACK_CLIENT_SECRET=your_client_secret_here
# SLACK_SIGNING_SECRET=your_signing_secret_here
# SECRET_KEY=your-secret-key-here
```

## 4. Get Slack Token

```bash
# Activate virtual environment
source venv/bin/activate

# Run OAuth flow
slack-mcp-server --oauth
```

This will:
1. Open your browser to Slack's authorization page
2. Ask you to install the app to your workspace
3. Display your bot token

## 5. Test the Server

```bash
# Set your bot token
export SLACK_BOT_TOKEN=xoxb-your-bot-token-here

# Run the example
python examples/basic_usage.py
```

## 6. Use with MCP Client

```python
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

server_params = StdioServerParameters(
    command="slack-mcp-server",
    args=["--token", "your_bot_token"]
)

async with stdio_client(server_params) as (read, write):
    async with ClientSession(read, write) as session:
        await session.initialize()
        
        # List channels
        channels = await session.read_resource("slack://channels")
        
        # Post a message
        result = await session.call_tool("post_message", {
            "channel": "#general",
            "text": "Hello from MCP!"
        })
```

## Available Resources

- `slack://channels` - List all channels
- `slack://users` - List all users
- `slack://workspace` - Workspace information
- `slack://channels/{id}/history` - Channel message history

## Available Tools

- `post_message` - Send messages to channels
- `get_channel_history` - Get message history
- `list_channels` - List accessible channels
- `get_user_info` - Get user information
- `list_users` - List workspace users

## Troubleshooting

### "No Slack token provided"
Make sure you've set the `SLACK_BOT_TOKEN` environment variable or pass it with `--token`.

### "Authentication failed"
Check that your bot token is valid and hasn't been revoked.

### "Channel not found"
Make sure your bot has been added to the channel you're trying to access.

### OAuth issues
- Verify your Client ID, Client Secret, and Signing Secret are correct
- Make sure the redirect URL is set to `http://localhost:8000/auth/slack/callback`
- Check that your Slack app has the required OAuth scopes

## Next Steps

- Read the full [README.md](README.md) for detailed documentation
- Check out more examples in the `examples/` directory
- Deploy using Docker with the provided `docker-compose.yml`

## Need Help?

- [GitHub Issues](https://github.com/aaronpaddy/slack-mcp-server/issues)
- [Documentation](https://github.com/aaronpaddy/slack-mcp-server/wiki)
