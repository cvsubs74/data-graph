"""Tools module for the vendor risk analysis agent."""

import os
import logging
import requests
from typing import Dict, Any
from bs4 import BeautifulSoup
from google.adk.tools.mcp_tool import MCPToolset, StreamableHTTPConnectionParams
from ..config import Config

logger = logging.getLogger(__name__)
logging.basicConfig(format="[%(levelname)s]: %(message)s", level=logging.INFO)

# Get configuration
configs = Config()

# Create MCP toolset with proper configuration for HTTP connection
mcp_toolset = MCPToolset(
    connection_params=StreamableHTTPConnectionParams(
        url=configs.MCP_SERVER_URL,
        headers={
            "Content-Type": "application/json",
            "Accept": "text/event-stream"
        },
        timeout=30
    )
)

def scrape_and_extract_vendor_data(url: str) -> Dict[str, Any]:
    """Scrapes a vendor's website and returns the raw content for LLM analysis.
    
    Args:
        url: URL of the vendor's website to analyze
        
    Returns:
        Dict[str, Any]: Raw content for the LLM to analyze
    """
    logger.info(f"Scraping vendor website from {url}")
    
    try:
        # Fetch the content from the URL
        response = requests.get(url)
        response.raise_for_status()
        
        # Parse the HTML content
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Extract text content
        website_text = soup.get_text(separator='\n', strip=True)
        
        # Return the raw text for the LLM to analyze
        result = {
            "url": url,
            "website_text": website_text,
            "status": "success"
        }
        
        logger.info("Successfully scraped vendor website")
        return result
        
    except Exception as e:
        logger.error(f"Error scraping vendor website: {str(e)}")
        return {
            "url": url,
            "error": str(e),
            "status": "error"
        }

# The MCP toolset automatically provides access to all tools exposed by the MCP server
# For example: mcp_toolset.get_risk_questions(), mcp_toolset.search_web(), etc.
