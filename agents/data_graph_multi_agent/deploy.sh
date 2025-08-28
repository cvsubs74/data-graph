#!/bin/bash

# Deployment script for data graph multi-agent system
# This script builds and deploys the updated agent with MCP tool integration fixes

echo "Starting deployment of data graph multi-agent system..."

# Set environment variables
export PROJECT_ID=$(gcloud config get-value project)
export SERVICE_NAME="data-graph-multi-agent"
export REGION="us-central1"
export MCP_SERVER_URL="https://data-graph-mcp-server-uc.a.run.app"

# Build the Docker image
echo "Building Docker image..."
gcloud builds submit --tag gcr.io/$PROJECT_ID/$SERVICE_NAME

# Deploy to Cloud Run
echo "Deploying to Cloud Run..."
gcloud run deploy $SERVICE_NAME \
  --image gcr.io/$PROJECT_ID/$SERVICE_NAME \
  --platform managed \
  --region $REGION \
  --allow-unauthenticated \
  --memory 2Gi \
  --cpu 2 \
  --set-env-vars="MCP_SERVER_URL=$MCP_SERVER_URL"

echo "Deployment completed successfully!"
echo "Service URL: https://$SERVICE_NAME-$REGION.a.run.app"
