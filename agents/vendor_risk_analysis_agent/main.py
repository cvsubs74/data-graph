"""Entry point for Cloud Run deployment of the Vendor Risk Analysis Agent."""

import os
import logging
import uvicorn
from google.adk.cli.fast_api import get_fast_api_app

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

# Get the directory where main.py is located
AGENT_DIR = os.path.dirname(os.path.abspath(__file__))
# Session service URI (SQLite database for sessions)
SESSION_SERVICE_URI = "sqlite:///./sessions.db"
# Allowed origins for CORS
ALLOWED_ORIGINS = ["http://localhost", "http://localhost:8080", "*"]
# Set web=True to serve the ADK web interface
SERVE_WEB_INTERFACE = True

# Get the FastAPI app instance
app = get_fast_api_app(
    agent_dir=AGENT_DIR,
    session_db_url=SESSION_SERVICE_URI,
    allow_origins=ALLOWED_ORIGINS,
    web=SERVE_WEB_INTERFACE,
)

# Add health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy", "agent": "vendor_risk_analysis_agent"}

if __name__ == "__main__":
    # Use the PORT environment variable provided by Cloud Run, defaulting to 8080
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
