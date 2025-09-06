#!/bin/bash

# Update Dockerfile to run web server for Cloud Run
echo "🔧 Updating Dockerfile for web server..."

# Change the CMD to run the web server
sed -i '' 's/CMD \["slack-mcp-server"\]/CMD ["python", "-m", "slack_mcp.web_server"]/' Dockerfile

echo "✅ Updated Dockerfile to run web server"
echo "📋 Checking the updated CMD:"
grep "CMD" Dockerfile
