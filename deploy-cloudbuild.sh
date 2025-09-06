#!/bin/bash

# Slack MCP Server - Google Cloud Build Deployment (No Local Docker)
set -e

echo "🚀 Deploying Slack MCP Server using Cloud Build..."

# Configuration
PROJECT_ID="slack-mcp-server-demo"
SERVICE_NAME="slack-mcp-server"
REGION="us-central1"

# Step 1: Set project
echo "📋 Setting up Google Cloud project..."
gcloud config set project $PROJECT_ID

# Step 2: Enable required services
echo "🔧 Enabling required services..."
gcloud services enable cloudbuild.googleapis.com
gcloud services enable run.googleapis.com
gcloud services enable containerregistry.googleapis.com

# Step 3: Build using Cloud Build (no local Docker needed)
echo "☁️ Building with Cloud Build..."
gcloud builds submit --tag gcr.io/$PROJECT_ID/$SERVICE_NAME .

# Step 4: Deploy to Cloud Run
echo "🚀 Deploying to Cloud Run..."
gcloud run deploy $SERVICE_NAME \
  --image gcr.io/$PROJECT_ID/$SERVICE_NAME \
  --platform managed \
  --region $REGION \
  --allow-unauthenticated \
  --port 8000 \
  --memory 512Mi \
  --cpu 1 \
  --min-instances 0 \
  --max-instances 10 \
  --set-env-vars "HOST=0.0.0.0" \
  --timeout 300

# Step 5: Get the URL
echo "🎉 Deployment complete!"
URL=$(gcloud run services describe $SERVICE_NAME --region=$REGION --format="value(status.url)")
echo "📱 Your app is live at: $URL"
echo ""
echo "🔑 Next steps:"
echo "1. Set up secrets for your Slack credentials"
echo "2. Update your Slack app redirect URL to: $URL/auth/slack/callback"
echo "3. Test your deployment!"
