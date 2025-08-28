"""Tools module for the data graph multi agent."""

import os
import logging
import requests
import json
from typing import Dict, Any, List, Optional
from bs4 import BeautifulSoup
from google.adk.tools.mcp_tool import MCPToolset, StreamableHTTPConnectionParams
from ..config import Config
from .graph_visualization import visualize_graph

# Get configuration
configs = Config()

# Configure logging
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

# Create a filtered MCP toolset with only metadata-related tools for Document Analysis agent
metadata_mcp_toolset = MCPToolset(
    connection_params=StreamableHTTPConnectionParams(
        url=configs.MCP_SERVER_URL,
        headers={
            "Content-Type": "application/json",
            "Accept": "text/event-stream"
        },
        timeout=30
    ),
    # Only include metadata-related tools
    tool_filter=[
        "get_entity_types",
        "get_entity_parameters",
        "get_relationship_ontology",
        "list_data_elements",
        "list_data_subject_types"
    ]
)

# Create a visualization-focused MCP toolset that excludes entity creation tools
visualization_mcp_toolset = MCPToolset(
    connection_params=StreamableHTTPConnectionParams(
        url=configs.MCP_SERVER_URL,
        headers={
            "Content-Type": "application/json",
            "Accept": "text/event-stream"
        },
        timeout=30
    ),
    # Only include tools needed for visualization and similarity checking
    # Exclude all entity creation, update, and deletion tools
    tool_filter=[
        # Metadata tools
        "get_entity_types",
        "get_entity_parameters",
        "get_relationship_ontology",
        
        # Retrieval tools
        "find_similar_entities",
        "get_asset",
        "get_processing_activity",
        "get_data_element",
        "get_data_subject_type",
        "get_vendor",
        "get_relationships",
        
        # List tools
        "list_assets",
        "list_processing_activities",
        "list_data_elements",
        "list_data_subject_types",
        "list_vendors",
        "list_all_relationships"
    ]
)


def scrape_and_extract_policy_data(url: str) -> Dict[str, Any]:
    """Scrapes a privacy policy from a URL and returns the raw content for LLM analysis.
    
    Args:
        url: URL of the privacy policy to analyze
        
    Returns:
        Dict[str, Any]: Raw content for the LLM to analyze
    """
    logger.info(f"Scraping privacy policy from {url}")
    
    try:
        # Fetch the content from the URL
        response = requests.get(url)
        response.raise_for_status()
        
        # Parse the HTML content
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Extract text content
        policy_text = soup.get_text(separator='\n', strip=True)
        
        # Return the raw text for the LLM to analyze
        result = {
            "url": url,
            "policy_text": policy_text,
            "status": "success"
        }
        
        logger.info("Successfully scraped privacy policy")
        return result
        
    except Exception as e:
        logger.error(f"Error scraping privacy policy: {str(e)}")
        return {
            "url": url,
            "error": str(e),
            "status": "error"
        }

def visualize_graph_data(graph_json: Dict[str, Any]) -> Dict[str, Any]:
    """Creates a visual representation of the graph data.
    
    Takes the JSON graph data and generates a visualization using the visualize_graph function.
    
    Args:
        graph_json: A dictionary containing the graph data in the format:
                    {
                      "nodes": [...],
                      "edges": [...],
                      "metadata": {...}
                    }
        
    Returns:
        Dict[str, Any]: Information about the generated visualization including the file path
    """
    logger.info("Creating graph visualization from JSON data")
    
    try:
        # Generate the visualization
        visualization_path = visualize_graph(graph_json)
        
        # Return information about the visualization
        result = {
            "status": "success",
            "message": "Graph visualization created successfully",
            "visualization_path": visualization_path,
            "timestamp": requests.utils.formatdate()
        }
        
        logger.info(f"Successfully created graph visualization at {visualization_path}")
        return result
        
    except Exception as e:
        logger.error(f"Error creating graph visualization: {str(e)}")
        return {
            "status": "error",
            "error": str(e)
        }
