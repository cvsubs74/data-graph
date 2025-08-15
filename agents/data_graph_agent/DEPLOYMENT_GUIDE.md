# Data Graph Agent Deployment Guide

This guide provides step-by-step instructions for deploying the Data Graph Agent to Google Cloud Run and testing it using the ADK UI.

## Prerequisites

1. Google Cloud account with billing enabled
2. Google Cloud CLI (`gcloud`) installed and configured
3. ADK CLI (`adk`) installed
4. Docker installed (for local testing)

## Deployment Options

You have two options for deploying the agent:

### Option 1: Using the ADK CLI (Recommended)

1. **Authenticate with Google Cloud**:
   ```bash
   gcloud auth login
   gcloud config set project YOUR_PROJECT_ID
   ```

2. **Set environment variables**:
   ```bash
   export GOOGLE_CLOUD_PROJECT="graph-rag-app-20250811"  # Your GCP project ID
   export GOOGLE_CLOUD_LOCATION="us-central1"  # Your preferred region
   ```

3. **Deploy using the ADK CLI**:
   ```bash
   adk deploy cloud_run \
     --project=$GOOGLE_CLOUD_PROJECT \
     --region=$GOOGLE_CLOUD_LOCATION \
     --service_name="data-graph-agent" \
     --with_ui \
     /path/to/data_graph_agent
   ```

4. **Allow unauthenticated invocations** when prompted (for UI testing)

### Option 2: Using the Deployment Script

1. **Update the script variables** if needed in `deploy_to_cloud_run.sh`
2. **Run the deployment script**:
   ```bash
   ./deploy_to_cloud_run.sh
   ```

### Option 3: Manual Deployment with Docker and Cloud Run

1. **Build the Docker image locally**:
   ```bash
   cd /path/to/data_graph_agent
   docker build -t data-graph-agent .
   ```

2. **Tag and push the image to Google Container Registry**:
   ```bash
   docker tag data-graph-agent gcr.io/$GOOGLE_CLOUD_PROJECT/data-graph-agent
   docker push gcr.io/$GOOGLE_CLOUD_PROJECT/data-graph-agent
   ```

3. **Deploy to Cloud Run**:
   ```bash
   gcloud run deploy data-graph-agent \
     --image gcr.io/$GOOGLE_CLOUD_PROJECT/data-graph-agent \
     --platform managed \
     --region $GOOGLE_CLOUD_LOCATION \
     --allow-unauthenticated
   ```

## UI Testing

After deployment, you can test your agent using the ADK UI:

1. **Access the UI**: Navigate to the Cloud Run service URL provided after deployment
   ```
   https://data-graph-agent-[hash].a.run.app
   ```

2. **Using the UI**:
   - Select your agent from the dropdown menu
   - Start a new conversation
   - Type messages to interact with your agent
   - View execution details in the UI

3. **Testing the API directly**:
   ```bash
   # Health check endpoint
   curl https://data-graph-agent-[hash].a.run.app/health
   
   # Agent API endpoint (replace with your actual service URL)
   curl -X POST \
     -H "Content-Type: application/json" \
     -d '{"message": "List all relationships", "session_id": "test-session"}' \
     https://data-graph-agent-[hash].a.run.app/api/agents/data_graph_agent/chat
   ```

## Troubleshooting

If you encounter issues:

1. **Check Cloud Run logs**:
   ```bash
   gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=data-graph-agent" --limit=10
   ```

2. **Verify environment variables** are correctly set in the Cloud Run service

3. **Test locally** before deploying:
   ```bash
   uvicorn main:app --host 0.0.0.0 --port 8080
   ```

## Additional Resources

- [ADK Documentation](https://google.github.io/adk-docs/)
- [Cloud Run Documentation](https://cloud.google.com/run/docs)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
