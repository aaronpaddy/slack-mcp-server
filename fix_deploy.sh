#!/bin/bash

# Fix the deployment script by removing PORT from env vars
echo "🔧 Fixing deployment script..."

# Remove PORT from the env vars
sed -i '' 's/--set-env-vars "HOST=0.0.0.0,PORT=8000"/--set-env-vars "HOST=0.0.0.0"/' deploy-cloudbuild.sh

echo "✅ Fixed deployment script - removed PORT env var"
echo "📋 Cloud Run will automatically set PORT environment variable"
