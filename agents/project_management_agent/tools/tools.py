"""Tools module for the project management agent."""

import os
import logging
import json
from typing import Dict, Any, List, Optional
from google.adk.tools.mcp_tool import MCPToolset, StreamableHTTPConnectionParams
from ..config import Config

logger = logging.getLogger(__name__)
logging.basicConfig(format="[%(levelname)s]: %(message)s", level=logging.INFO)

# Get configuration
configs = Config()

# Create MCP toolset with proper configuration for HTTP connection
mcp_toolset = MCPToolset(
    connection_params=StreamableHTTPConnectionParams(
        url="https://data-graph-mcp-server-79797180773.us-central1.run.app/mcp",
        headers={
            "Content-Type": "application/json",
            "Accept": "text/event-stream"
        },
        timeout=30
    )
)

# Create a filtered MCP toolset with only metadata-related tools for Entity Detector agent
metadata_mcp_toolset = MCPToolset(
    connection_params=StreamableHTTPConnectionParams(
        url="https://data-graph-mcp-server-79797180773.us-central1.run.app/mcp",
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
        "find_similar_entities"
    ]
)

def parse_document(document_content: str) -> Dict[str, Any]:
    """Parses a document and returns the processed content for LLM analysis.
    
    Args:
        document_content: Raw text content of the document to analyze
        
    Returns:
        Dict[str, Any]: Processed content for the LLM to analyze
    """
    logger.info("Processing document content")
    
    try:
        # Process the document content
        # This is a simple implementation that just returns the raw content
        # In a real implementation, you might want to do more processing
        # such as removing irrelevant elements, formatting text, identifying sections, etc.
        
        # Return the processed text for the LLM to analyze
        result = {
            "document_text": document_content,
            "status": "success"
        }
        
        logger.info("Successfully processed document")
        return result
        
    except Exception as e:
        logger.error(f"Error processing document: {str(e)}")
        return {
            "error": str(e),
            "status": "error"
        }

