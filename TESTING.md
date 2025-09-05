# 🧪 Testing Guide

This guide covers different ways to test the Slack MCP Server, from basic functionality to full integration testing.

## 🚀 Quick Tests (No Slack Required)

### 1. Installation Test
```bash
# Activate virtual environment
source venv/bin/activate

# Test CLI is working
slack-mcp-server --version
slack-mcp-server --help
```

### 2. Unit Tests
```bash
# Install test dependencies
pip install pytest pytest-asyncio

# Run all tests
python -m pytest tests/ -v

# Run with coverage (if installed)
python -m pytest tests/ --cov=slack_mcp --cov-report=html
```

### 3. Configuration Test
```bash
# Test configuration loading
python -c "from slack_mcp.config import get_settings; print('Config loaded successfully')"

# Test with environment variables
SLACK_CLIENT_ID=test python -c "from slack_mcp.config import get_settings; s=get_settings(); print(f'Client ID: {s.slack_client_id}')"
```

## 🔧 Integration Tests (Requires Slack Setup)

### Prerequisites
1. Create a Slack app at https://api.slack.com/apps
2. Add required OAuth scopes:
   - `channels:read`
   - `groups:read` 
   - `chat:write`
   - `users:read`
   - `team:read`
3. Set redirect URL: `http://localhost:8000/auth/slack/callback`

### 1. OAuth Flow Test
```bash
# Set up environment
cp .env.example .env
# Edit .env with your Slack app credentials

# Test OAuth flow
slack-mcp-server --oauth
```

### 2. Server Connection Test
```bash
# Get your bot token from OAuth flow above
export SLACK_BOT_TOKEN=xoxb-your-token-here

# Test server startup (will show connection status)
slack-mcp-server --token $SLACK_BOT_TOKEN --log-level INFO
```

### 3. MCP Client Test
```bash
# Run the example script
python examples/basic_usage.py
```

## 🐳 Docker Tests

### 1. Build Test
```bash
# Build the Docker image
docker build -t slack-mcp-server .

# Test the built image
docker run --rm slack-mcp-server --version
```

### 2. Docker Compose Test
```bash
# Set environment variables
export SLACK_BOT_TOKEN=your-token-here
export SLACK_CLIENT_ID=your-client-id
export SLACK_CLIENT_SECRET=your-client-secret
export SLACK_SIGNING_SECRET=your-signing-secret

# Start with docker-compose
docker-compose up -d

# Check logs
docker-compose logs

# Stop
docker-compose down
```

## 🔍 Manual Testing Scenarios

### Test 1: List Resources
```python
import asyncio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def test_resources():
    server_params = StdioServerParameters(
        command="slack-mcp-server",
        args=["--token", "your-token-here"]
    )
    
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            resources = await session.list_resources()
            print(f"Found {len(resources.resources)} resources")
            for r in resources.resources:
                print(f"  - {r.name}: {r.uri}")

asyncio.run(test_resources())
```

### Test 2: Read Channel Data
```python
async def test_read_channels():
    # ... (same setup as above)
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            result = await session.read_resource("slack://channels")
            print("Channels data:", result.contents[0].text[:200] + "...")

asyncio.run(test_read_channels())
```

### Test 3: Use Tools
```python
async def test_tools():
    # ... (same setup as above)
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            
            # List channels
            result = await session.call_tool("list_channels", {"limit": 5})
            print("List channels result:", result.content[0].text[:200])
            
            # Post message (be careful with this!)
            # result = await session.call_tool("post_message", {
            #     "channel": "#test",
            #     "text": "Hello from MCP test!"
            # })

asyncio.run(test_tools())
```

## 🚨 Error Testing

### Test Invalid Token
```bash
# Should show authentication error
slack-mcp-server --token "xoxb-invalid-token" --log-level DEBUG
```

### Test Missing Permissions
```bash
# Remove some OAuth scopes from your Slack app and test
# Should show permission errors for certain operations
```

### Test Network Issues
```bash
# Test with no internet connection
# Should show connection errors gracefully
```

## 📊 Performance Testing

### Load Test Resources
```python
import asyncio
import time

async def load_test():
    # Test multiple concurrent resource reads
    tasks = []
    for i in range(10):
        tasks.append(test_read_channels())
    
    start = time.time()
    await asyncio.gather(*tasks)
    end = time.time()
    print(f"10 concurrent requests took {end-start:.2f} seconds")

asyncio.run(load_test())
```

## 🔧 Debugging Tips

### Enable Debug Logging
```bash
slack-mcp-server --token $SLACK_BOT_TOKEN --log-level DEBUG
```

### Check Slack API Responses
```python
# Add this to slack_client.py for debugging
import json
print(json.dumps(response.data, indent=2))
```

### Test Individual Components
```python
# Test Slack client directly
from slack_mcp.slack_client import SlackClient
client = SlackClient("your-token")
channels = await client.list_channels()
print(f"Found {len(channels)} channels")
```

## ✅ Test Checklist

Before considering the server ready for production:

- [ ] All unit tests pass
- [ ] OAuth flow works end-to-end
- [ ] Can connect to Slack successfully
- [ ] All MCP resources return data
- [ ] All MCP tools work correctly
- [ ] Error handling works for invalid tokens
- [ ] Error handling works for missing permissions
- [ ] Docker build succeeds
- [ ] Docker container runs correctly
- [ ] Example script works
- [ ] Performance is acceptable under load

## 🆘 Troubleshooting

### Common Issues

**"No module named slack_mcp"**
- Make sure you've installed with `pip install -e .`

**"Authentication failed"**
- Check your bot token is valid
- Verify token hasn't been revoked
- Ensure token starts with `xoxb-`

**"Channel not found"**
- Make sure bot is added to the channel
- Use channel ID instead of name
- Check bot has required permissions

**"Permission denied"**
- Verify OAuth scopes in Slack app settings
- Reinstall app to workspace if scopes changed

**MCP connection issues**
- Check server is running
- Verify stdio communication is working
- Enable debug logging to see detailed errors

Need more help? Check the [GitHub Issues](https://github.com/aaronpaddy/slack-mcp-server/issues) or create a new one!
