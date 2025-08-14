#!/bin/bash

# Exit immediately if a command exits with a non-zero status.
set -e

# --- Configuration ---
PROJECT_ID="graph-rag-app-20250811"
REGION="us-central1"

echo "==================================================="
echo "Privacy Data Governance Graph - Deployment Script"
echo "==================================================="
echo "Project ID: $PROJECT_ID"
echo "Region: $REGION"
echo ""

# --- Helper Function for Cloud Function Deployment ---
deploy_function() {
  local function_name=$1
  local function_dir="backend/$1"
  local entry_point=$2
  local extra_args=$3

  echo "-----------------------------------------------------"
  echo "Deploying Cloud Function: $function_name..."
  echo "-----------------------------------------------------"

  # Create a temporary build directory with all necessary files
  local build_dir="/tmp/build_$function_name"
  rm -rf "$build_dir"
  mkdir -p "$build_dir"

  # Copy function-specific files
  echo "Copying function files from $function_dir..."
  cp -R "$function_dir/." "$build_dir/"
  
  # Copy the shared services directory
  echo "Copying shared services..."
  cp -R "backend/services" "$build_dir/"

  # Verify the build structure
  echo "Build directory structure:"
  ls -la "$build_dir/"
  echo "Services directory:"
  ls -la "$build_dir/services/"

  # Environment variables
  local env_vars="GCP_PROJECT=$PROJECT_ID"

  echo "Deploying $function_name to Google Cloud Functions..."
  gcloud functions deploy "$function_name" \
    --project="$PROJECT_ID" \
    --gen2 \
    --runtime=python311 \
    --region="$REGION" \
    --source="$build_dir" \
    --entry-point="$entry_point" \
    --set-env-vars="$env_vars" \
    --trigger-http \
    --allow-unauthenticated \
    --memory=1GiB \
    --timeout=540s \
    $extra_args

  # Clean up
  rm -rf "$build_dir"
  echo "Deployment for $function_name complete."
  echo "-----------------------------------------------------"
}

# --- Helper Function for MCP Server Deployment ---
deploy_mcp() {
  echo "-----------------------------------------------------"
  echo "Deploying Privacy Data Graph MCP server..."
  echo "-----------------------------------------------------"
  
  # Create a temporary build directory with all necessary files
  local build_dir="/tmp/build_mcp"
  rm -rf "$build_dir"
  mkdir -p "$build_dir"
  
  # Copy MCP server files
  echo "Copying MCP function files..."
  cp -R "backend/mcp_function/"* "$build_dir/"
  
  # Copy the shared services directory
  echo "Copying shared services..."
  cp -R "backend/services" "$build_dir/"
  
  # Verify the build structure
  echo "Build directory structure:"
  ls -la "$build_dir/"
  echo "Services directory:"
  ls -la "$build_dir/services/"
  
  # Environment variables
  local env_vars="GCP_PROJECT=$PROJECT_ID"
  
  echo "Deploying MCP server to Google Cloud Run..."
  gcloud run deploy "mcp-server" \
    --project="$PROJECT_ID" \
    --region="$REGION" \
    --source="$build_dir" \
    --set-env-vars="$env_vars" \
    --allow-unauthenticated \
    --memory=1Gi \
    --cpu=1 \
    --timeout=540s \
    --port=8080 \
    --platform=managed \
    --clear-base-image
  
  # Clean up
  rm -rf "$build_dir"
  
  echo "Deployment for MCP server complete."
  echo "-----------------------------------------------------"
}

# --- Main Deployment Logic ---
deploy_backend() {
    local specific_function=$1
    
    echo "Starting backend deployment..."
    
    if [ -z "$specific_function" ]; then
        # Deploy all functions in parallel
        echo "Deploying all backend functions in parallel..."
        
        deploy_function "ingest_function" "ingest_document" "" &
        local ingest_pid=$!
        
        deploy_mcp &
        local mcp_pid=$!
        
        # Wait for all deployments to finish
        echo "Waiting for all backend functions to deploy..."
        wait $ingest_pid $mcp_pid
        echo "All backend functions deployed successfully!"
        
    elif [ "$specific_function" == "ingest" ]; then
        deploy_function "ingest_function" "ingest_document" ""
    elif [ "$specific_function" == "mcp" ]; then
        deploy_mcp
    else
        echo "Error: Unknown function '$specific_function'. Valid options are: ingest, mcp"
        exit 1
    fi
}

# --- Test Deployment ---
test_deployment() {
    echo "-----------------------------------------------------"
    echo "Testing deployed functions..."
    echo "-----------------------------------------------------"
    
    # Get function URLs
    local ingest_url=$(gcloud functions describe ingest_function --region=$REGION --project=$PROJECT_ID --format="value(serviceConfig.uri)" 2>/dev/null || echo "")
    local mcp_url=$(gcloud run services describe mcp-server --region=$REGION --project=$PROJECT_ID --format="value(status.url)" 2>/dev/null || echo "")
    
    echo "Function URLs:"
    if [ -n "$ingest_url" ]; then
        echo "  Ingest Function: $ingest_url"
        echo "  Testing ingest function health..."
        curl -s "$ingest_url" -X OPTIONS || echo "  Health check failed"
    fi
    
    if [ -n "$mcp_url" ]; then
        echo "  MCP Server (Cloud Run): $mcp_url"
        echo "  Testing MCP server health..."
        curl -s "$mcp_url/health" || echo "  Health check failed"
    fi
    
    echo "-----------------------------------------------------"
}

# --- Usage Information ---
show_usage() {
    echo "Usage: $0 [backend [function_name]|test|help]"
    echo ""
    echo "Commands:"
    echo "  backend          - Deploy all backend functions (ingest + mcp)"
    echo "  backend ingest   - Deploy only the ingest function"
    echo "  backend mcp      - Deploy only the MCP function"
    echo "  test            - Test deployed functions"
    echo "  help            - Show this help message"
    echo ""
    echo "Examples:"
    echo "  ./deploy.sh                    # Deploy all backend functions"
    echo "  ./deploy.sh backend            # Deploy all backend functions"
    echo "  ./deploy.sh backend ingest     # Deploy only ingest function"
    echo "  ./deploy.sh backend mcp        # Deploy only MCP function"
    echo "  ./deploy.sh test              # Test deployed functions"
}

# --- Main Script Logic ---
if [[ "$1" == "backend" && -z "$2" ]]; then
    deploy_backend
elif [[ "$1" == "backend" && -n "$2" ]]; then
    deploy_backend "$2"
elif [ "$1" == "test" ]; then
    test_deployment
elif [ "$1" == "help" ] || [ "$1" == "--help" ] || [ "$1" == "-h" ]; then
    show_usage
elif [ -z "$1" ]; then
    # Default to deploying all backend functions
    deploy_backend
else
    echo "Error: Unknown command '$1'"
    echo ""
    show_usage
    exit 1
fi

echo ""
echo "==================================================="
echo "Deployment script completed!"
echo "==================================================="
