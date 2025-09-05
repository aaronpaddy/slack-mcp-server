# 🚀 Slack MCP Server

A **Model Context Protocol (MCP)** server that provides seamless integration with Slack workspaces. This server allows AI agents and applications to interact with Slack channels, users, and messages through the standardized MCP protocol.

## ✨ Features

### 🔌 MCP Resources
- **Channels**: List and access all Slack channels
- **Messages**: Read message history from channels
- **Users**: Access user directory and information
- **Workspace**: Get workspace details and metadata

### 🛠️ MCP Tools
- **Post Messages**: Send messages to channels and threads
- **Channel History**: Retrieve message history with filtering
- **List Channels**: Get all accessible channels
- **User Info**: Fetch detailed user information
- **List Users**: Get workspace user directory
- **Search Messages**: Search across workspace messages (coming soon)

### 🔐 Authentication
- **OAuth 2.0**: Secure Slack workspace authorization
- **Token Management**: Secure token storage and validation
- **Multi-workspace**: Support for multiple Slack workspaces

## 🚀 Quick Start

### Prerequisites
- Python 3.11 or higher
- A Slack workspace where you can install apps
- Slack app credentials (Client ID, Client Secret, Signing Secret)

### 1. Installation

```bash
# Clone the repository
git clone https://github.com/aaronpaddy/slack-mcp-server.git
cd slack-mcp-server

# Install dependencies
pip install -e .

# Or using Poetry
poetry install
```

### 2. Slack App Setup

1. Go to [Slack API](https://api.slack.com/apps) and create a new app
2. Configure OAuth & Permissions with these scopes:
   - `channels:read` - View basic information about public channels
   - `groups:read` - View basic information about private channels
   - `chat:write` - Send messages as the app
   - `users:read` - View people in the workspace
   - `team:read` - View workspace information

3. Set the redirect URL to: `http://localhost:8000/auth/slack/callback`

4. Note down your:
   - Client ID
   - Client Secret  
   - Signing Secret

### 3. Configuration

Create a `.env` file:

```bash
# Copy the example environment file
cp .env.example .env

# Edit with your Slack app credentials
SLACK_CLIENT_ID=your_client_id_here
SLACK_CLIENT_SECRET=your_client_secret_here
SLACK_SIGNING_SECRET=your_signing_secret_here
SECRET_KEY=your-secret-key-here
```

### 4. Get Slack Token

Run the OAuth flow to authorize your workspace:

```bash
slack-mcp-server --oauth
```

This will:
1. Start a local web server
2. Open your browser to Slack's authorization page
3. Handle the OAuth callback
4. Display your bot token

### 5. Run the Server

```bash
# Using the token from OAuth
slack-mcp-server --token your_bot_token_here

# Or set environment variable
export SLACK_BOT_TOKEN=your_bot_token_here
slack-mcp-server
```

## 🐳 Docker Deployment

### Using Docker Compose

```bash
# Set environment variables
export SLACK_CLIENT_ID=your_client_id
export SLACK_CLIENT_SECRET=your_client_secret
export SLACK_SIGNING_SECRET=your_signing_secret
export SLACK_BOT_TOKEN=your_bot_token

# Start the server
docker-compose up -d
```

### Using Docker

```bash
# Build the image
docker build -t slack-mcp-server .

# Run the container
docker run -d \\
  --name slack-mcp-server \\
  -p 8000:8000 \\
  -e SLACK_BOT_TOKEN=your_bot_token \\
  slack-mcp-server
```

## 📖 Usage Examples

### Using with MCP Client

```python
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

# Connect to the Slack MCP server
server_params = StdioServerParameters(
    command="slack-mcp-server",
    args=["--token", "your_bot_token"]
)

async with stdio_client(server_params) as (read, write):
    async with ClientSession(read, write) as session:
        # Initialize the connection
        await session.initialize()
        
        # List available resources
        resources = await session.list_resources()
        print("Available resources:", resources)
        
        # Read channel list
        channels = await session.read_resource("slack://channels")
        print("Channels:", channels)
        
        # Post a message
        result = await session.call_tool("post_message", {
            "channel": "#general",
            "text": "Hello from MCP!"
        })
        print("Message posted:", result)
```

### Available Resources

- `slack://channels` - List all channels
- `slack://users` - List all users  
- `slack://workspace` - Workspace information
- `slack://channels/{channel_id}` - Specific channel info
- `slack://channels/{channel_id}/history` - Channel message history

### Available Tools

- `post_message` - Send a message to a channel
- `get_channel_history` - Get message history from a channel
- `list_channels` - List all accessible channels
- `get_user_info` - Get information about a user
- `list_users` - List all workspace users
- `search_messages` - Search messages (coming soon)

## 🔧 Development

### Setup Development Environment

```bash
# Clone and install in development mode
git clone https://github.com/aaronpaddy/slack-mcp-server.git
cd slack-mcp-server
pip install -e ".[dev]"

# Install pre-commit hooks
pre-commit install
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=slack_mcp

# Run specific test file
pytest tests/test_slack_client.py
```

### Code Quality

```bash
# Format code
black src/ tests/

# Lint code
ruff check src/ tests/

# Type checking
mypy src/
```

## 📚 API Reference

### MCP Resources

#### `slack://channels`
Returns a JSON array of all accessible channels with their metadata.

#### `slack://users`  
Returns a JSON array of all workspace users with their information.

#### `slack://workspace`
Returns workspace information including name, domain, and settings.

#### `slack://channels/{channel_id}/history`
Returns message history from the specified channel.

### MCP Tools

#### `post_message`
Post a message to a Slack channel.

**Parameters:**
- `channel` (string): Channel ID or name (e.g., "#general")
- `text` (string): Message text to post
- `thread_ts` (string, optional): Reply to a thread

#### `get_channel_history`
Retrieve message history from a channel.

**Parameters:**
- `channel` (string): Channel ID or name
- `limit` (integer): Number of messages (default: 50, max: 1000)
- `oldest` (string, optional): Only messages after this timestamp
- `latest` (string, optional): Only messages before this timestamp

## 🔒 Security

- All tokens are handled securely and never logged
- OAuth 2.0 flow with state validation
- Input validation on all endpoints
- Rate limiting protection
- Secure defaults for all configurations

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- **Issues**: [GitHub Issues](https://github.com/aaronpaddy/slack-mcp-server/issues)
- **Discussions**: [GitHub Discussions](https://github.com/aaronpaddy/slack-mcp-server/discussions)
- **Documentation**: [Wiki](https://github.com/aaronpaddy/slack-mcp-server/wiki)

## 🙏 Acknowledgments

- [Anthropic](https://anthropic.com) for the Model Context Protocol
- [Slack](https://slack.com) for their excellent API
- The open-source community for inspiration and contributions

---

**Made with ❤️ for the AI and automation community**
