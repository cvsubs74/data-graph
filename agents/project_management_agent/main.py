"""Main module for the project management multi-agent system."""

import logging
import os
from typing import Dict, Any, List, Optional
from google.adk.rest import create_app
from google.adk.run import Runner
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Import the root agent from agent.py
from .agent import root_agent

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Create the FastAPI app with the agent
app = create_app(root_agent)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}

def main() -> None:
    """Main entry point for the project management multi-agent system."""
    # Create a runner for the agent
    runner = Runner(root_agent)
    
    # Run the agent
    runner.run(
        "Hello! I'm the Project Management Coordinator for privacy governance. "
        "I coordinate a team of specialized agents to help you analyze projects by processing documents, "
        "detecting entities, and providing insights for privacy governance. "
        "To get started, please provide a document URL or tell me about your project."
    )

if __name__ == "__main__":
    # Check if we should run as a server or as a CLI
    if os.environ.get("RUN_SERVER", "0") == "1":
        import uvicorn
        
        # Get port from environment variable or use default
        port = int(os.environ.get("PORT", 8080))
        
        # Run the server
        uvicorn.run(app, host="0.0.0.0", port=port)
    else:
        # Run as CLI
        main()
