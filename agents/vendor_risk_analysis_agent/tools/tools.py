"""Tools module for the vendor risk analysis agent."""

import os
import logging
import requests
import validators
from typing import Dict, Any, Tuple, Optional
from bs4 import BeautifulSoup
from urllib.parse import urlparse
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

def validate_url(url: str) -> Dict[str, Any]:
    """
Validates if a URL is properly formatted and accessible.

Args:
    url: URL to validate
    
Returns:
    Dict[str, Any]: Validation results including status and details
    """
    logger.info(f"Validating URL: {url}")
    
    result = {
        "url": url,
        "is_valid": False,
        "status": "error",
        "details": ""
    }
    
    # Check if URL format is valid
    if not validators.url(url):
        result["details"] = "Invalid URL format. Please provide a complete URL including http:// or https://"
        return result
    
    # Check if domain exists and URL is accessible
    try:
        # Parse URL to get domain
        parsed_url = urlparse(url)
        domain = parsed_url.netloc
        
        # Attempt to connect to the URL
        response = requests.head(url, timeout=10)
        
        # Check if response is successful
        if response.status_code < 400:
            result["is_valid"] = True
            result["status"] = "success"
            result["details"] = f"URL is valid and accessible. Status code: {response.status_code}"
            result["domain"] = domain
        else:
            result["details"] = f"URL exists but returned an error. Status code: {response.status_code}"
    
    except requests.exceptions.ConnectionError:
        result["details"] = "Could not connect to the URL. Please check if the domain exists and is accessible."
    except requests.exceptions.Timeout:
        result["details"] = "Connection timed out. The server might be slow or unavailable."
    except requests.exceptions.RequestException as e:
        result["details"] = f"An error occurred while accessing the URL: {str(e)}"
    
    logger.info(f"URL validation result: {result['status']} - {result['details']}")
    return result

# The MCP toolset automatically provides access to all tools exposed by the MCP server
# For example: mcp_toolset.get_risk_questions(), mcp_toolset.search_web(), etc.
