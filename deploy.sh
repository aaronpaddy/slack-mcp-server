#!/bin/bash

# Slack MCP Server - Google Cloud Deployment Script
set -e

echo "🚀 Deploying Slack MCP Server to Google Cloud Run..."

# Configuration
PROJECT_ID="slack-mcp-server-demo"
SERVICE_NAME="slack-mcp-server"
REGION="us-central1"
IMAGE_NAME="gcr.io/${PROJECT_ID}/${SERVICE_NAME}"

# Step 1: Set project
echo "📋 Setting up Google Cloud project..."
gcloud config set project $PROJECT_ID

# Step 2: Build and push Docker image
echo "🐳 Building Docker image..."
docker build -t $IMAGE_NAME .

echo "📤 Pushing to Google Container Registry..."
docker push $IMAGE_NAME

# Step 3: Deploy to Cloud Run
echo "☁️  Deploying to Cloud Run..."
gcloud run deploy $SERVICE_NAME \
  --image $IMAGE_NAME \
  --platform managed \
  --region $REGION \
  --allow-unauthenticated \
  --port 8000 \
  --memory 512Mi \
  --cpu 1 \
  --min-instances 0 \
  --max-instances 10 \
  --set-env-vars "HOST=0.0.0.0,PORT=8000" \
  --timeout 300

# Step 4: Get the URL
echo "🎉 Deployment complete!"
URL=$(gcloud run services describe $SERVICE_NAME --region=$REGION --format="value(status.url)")
echo "📱 Your app is live at: $URL"
echo ""
echo "🔑 Next steps:"
echo "1. Set up secrets for your Slack credentials"
echo "2. Update your Slack app redirect URL to: $URL/auth/slack/callback"
echo "3. Test your deployment!"

