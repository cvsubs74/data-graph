import asyncio
import json
import logging
import os
from typing import List, Dict, Any

from fastmcp import FastMCP

# Import our data service
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from services.data_graph_service import DataGraphService

logger = logging.getLogger(__name__)
logging.basicConfig(format="[%(levelname)s]: %(message)s", level=logging.INFO)

mcp = FastMCP("Privacy Data Governance Graph MCP Server")

# Initialize data service
try:
    data_service = DataGraphService()
    logger.info("DataGraphService initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize DataGraphService: {e}")
    data_service = None

@mcp.tool()
def create_asset(name: str, description: str = None, properties: Dict[str, Any] = None) -> str:
    """
    Creates a new asset in the privacy data governance graph.
    
    Args:
        name: Name of the asset (required)
        description: Optional description of the asset
        properties: Optional dictionary of additional properties
    
    Returns:
        The unique asset_id of the created asset
    """
    logger.info(f">>> 🛠️ Tool: 'create_asset' called with name='{name}'")
    if not data_service:
        return ""
    try:
        # Ensure properties is a valid JSON-serializable dictionary
        json_properties = None
        if properties:
            try:
                # Convert properties to a JSON string to ensure it's serializable
                json_properties = json.dumps(properties)
                # Then parse it back to a dict to ensure it's valid
                json_properties = json.loads(json_properties)
            except (TypeError, ValueError) as e:
                logger.error(f"Properties not JSON serializable: {e}")
                # Fall back to a simple string representation
                json_properties = {"raw_properties": str(properties)}
                
        return data_service.create_asset(name=name, description=description, properties=json_properties)
    except Exception as e:
        logger.error(f"Error creating asset: {e}")
        return ""

@mcp.tool()
def get_asset(asset_id: str) -> Dict[str, Any]:
    """
    Retrieves details of a specific asset by its ID.
    
    Args:
        asset_id: The unique identifier of the asset
    
    Returns:
        A dictionary with the asset's details or empty dict if not found
    """
    logger.info(f">>> 🛠️ Tool: 'get_asset' called with asset_id='{asset_id}'")
    if not data_service:
        return {}
    try:
        result = data_service.get_asset(asset_id)
        return result if result else {}
    except Exception as e:
        logger.error(f"Error getting asset: {e}")
        return {}

@mcp.tool()
def update_asset(asset_id: str, name: str = None, description: str = None, properties: Dict[str, Any] = None) -> bool:
    """
    Updates an existing asset with new information.
    
    Args:
        asset_id: The unique identifier of the asset to update
        name: Optional new name for the asset
        description: Optional new description for the asset
        properties: Optional new properties dictionary
    
    Returns:
        True if the update was successful, False otherwise
    """
    logger.info(f">>> 🛠️ Tool: 'update_asset' called with asset_id='{asset_id}'")
    if not data_service:
        return False
    try:
        return data_service.update_asset(asset_id=asset_id, name=name, description=description, properties=properties)
    except Exception as e:
        logger.error(f"Error updating asset: {e}")
        return False

@mcp.tool()
def delete_asset(asset_id: str) -> bool:
    """
    Deletes an asset from the privacy data governance graph.
    
    Args:
        asset_id: The unique identifier of the asset to delete
    
    Returns:
        True if the deletion was successful, False otherwise
    """
    logger.info(f">>> 🛠️ Tool: 'delete_asset' called with asset_id='{asset_id}'")
    if not data_service:
        return False
    try:
        return data_service.delete_asset(asset_id)
    except Exception as e:
        logger.error(f"Error deleting asset: {e}")
        return False

@mcp.tool()
def list_assets(limit: int = 100) -> List[Dict[str, Any]]:
    """
    Retrieves all assets from the privacy data governance graph.
    
    Args:
        limit: Maximum number of assets to return (default: 100)
    
    Returns:
        A list of asset dictionaries with details like asset_id, name, description, properties, etc.
    """
    logger.info(f">>> 🛠️ Tool: 'list_assets' called with limit={limit}")
    if not data_service:
        return []
    try:
        return data_service.list_assets(limit=limit)
    except Exception as e:
        logger.error(f"Error listing assets: {e}")
        return []

@mcp.tool()
def create_processing_activity(name: str, description: str = None, purpose: str = None, legal_basis: str = None, properties: Dict[str, Any] = None) -> str:
    """
    Creates a new processing activity in the privacy data governance graph.
    
    Args:
        name: Name of the processing activity (required)
        description: Optional description of the processing activity
        purpose: Optional purpose of the processing activity
        legal_basis: Optional legal basis for the processing activity
        properties: Optional dictionary of additional properties
    
    Returns:
        The unique activity_id of the created processing activity
    """
    logger.info(f">>> 🛠️ Tool: 'create_processing_activity' called with name='{name}'")
    if not data_service:
        return ""
    try:
        # Merge purpose and legal_basis into properties
        merged_properties = {}
        if properties and isinstance(properties, dict):
            merged_properties.update(properties)
        elif properties:
            # Handle non-dict properties by converting to string
            merged_properties["raw_properties"] = str(properties)
            
        # Add purpose and legal_basis to properties
        if purpose:
            merged_properties["purpose"] = purpose
        if legal_basis:
            merged_properties["legal_basis"] = legal_basis
            
        # Ensure properties is JSON serializable
        json_properties = None
        if merged_properties:
            try:
                # Convert to JSON string and back to ensure it's serializable
                json_properties = json.dumps(merged_properties)
                json_properties = json.loads(json_properties)
            except (TypeError, ValueError) as e:
                logger.error(f"Properties not JSON serializable: {e}")
                # Fall back to a simple string representation
                json_properties = {"raw_properties": str(merged_properties)}
            
        return data_service.create_processing_activity(
            name=name, description=description, properties=json_properties
        )
    except Exception as e:
        logger.error(f"Error creating processing activity: {e}")
        return ""

@mcp.tool()
def get_processing_activity(activity_id: str) -> Dict[str, Any]:
    """
    Retrieves details of a specific processing activity by its ID.
    
    Args:
        activity_id: The unique identifier of the processing activity
    
    Returns:
        A dictionary with the processing activity's details or empty dict if not found
    """
    logger.info(f">>> 🛠️ Tool: 'get_processing_activity' called with activity_id='{activity_id}'")
    if not data_service:
        return {}
    try:
        result = data_service.get_processing_activity(activity_id)
        return result if result else {}
    except Exception as e:
        logger.error(f"Error getting processing activity: {e}")
        return {}

@mcp.tool()
def list_processing_activities(limit: int = 100) -> List[Dict[str, Any]]:
    """
    Retrieves all processing activities from the privacy data governance graph.
    
    Args:
        limit: Maximum number of processing activities to return (default: 100)
    
    Returns:
        A list of processing activity dictionaries
    """
    logger.info(f">>> 🛠️ Tool: 'list_processing_activities' called with limit={limit}")
    if not data_service:
        return []
    try:
        return data_service.list_processing_activities(limit=limit)
    except Exception as e:
        logger.error(f"Error listing processing activities: {e}")
        return []

@mcp.tool()
def delete_processing_activity(activity_id: str) -> bool:
    """
    Deletes a processing activity from the privacy data governance graph.
    
    Args:
        activity_id: The unique identifier of the processing activity to delete
    
    Returns:
        True if the deletion was successful, False otherwise
    """
    logger.info(f">>> 🛠️ Tool: 'delete_processing_activity' called with activity_id='{activity_id}'")
    if not data_service:
        return False
    try:
        return data_service.delete_processing_activity(activity_id)
    except Exception as e:
        logger.error(f"Error deleting processing activity: {e}")
        return False

@mcp.tool()
def create_data_element(name: str, description: str = None, data_type: str = None, properties: Dict[str, Any] = None) -> str:
    """
    Creates a new data element in the privacy data governance graph.
    
    Args:
        name: Name of the data element (required)
        description: Optional description of the data element
        data_type: Optional type of data (e.g., PII, sensitive)
        properties: Optional dictionary of additional properties
    
    Returns:
        The unique element_id of the created data element
    """
    logger.info(f">>> 🛠️ Tool: 'create_data_element' called with name='{name}'")
    if not data_service:
        return ""
    try:
        # Merge data_type into properties if provided
        merged_properties = {}
        if properties and isinstance(properties, dict):
            merged_properties.update(properties)
        elif properties:
            merged_properties["raw_properties"] = str(properties)
            
        if data_type:
            merged_properties['data_type'] = data_type
            
        # Ensure properties is JSON serializable
        json_properties = None
        if merged_properties:
            try:
                # Convert to JSON string and back to ensure it's serializable
                json_properties = json.dumps(merged_properties)
                json_properties = json.loads(json_properties)
            except (TypeError, ValueError) as e:
                logger.error(f"Properties not JSON serializable: {e}")
                # Fall back to a simple string representation
                json_properties = {"raw_properties": str(merged_properties)}
            
        return data_service.create_data_element(
            name=name, description=description, properties=json_properties
        )
    except Exception as e:
        logger.error(f"Error creating data element: {e}")
        return ""

@mcp.tool()
def get_data_element(element_id: str) -> Dict[str, Any]:
    """
    Retrieves details of a specific data element by its ID.
    
    Args:
        element_id: The unique identifier of the data element
    
    Returns:
        A dictionary with the data element's details or empty dict if not found
    """
    logger.info(f">>> 🛠️ Tool: 'get_data_element' called with element_id='{element_id}'")
    if not data_service:
        return {}
    try:
        result = data_service.get_data_element(element_id)
        return result if result else {}
    except Exception as e:
        logger.error(f"Error getting data element: {e}")
        return {}

@mcp.tool()
def list_data_elements(limit: int = 100) -> List[Dict[str, Any]]:
    """
    Retrieves all data elements from the privacy data governance graph.
    
    Args:
        limit: Maximum number of data elements to return (default: 100)
    
    Returns:
        A list of data element dictionaries
    """
    logger.info(f">>> 🛠️ Tool: 'list_data_elements' called with limit={limit}")
    if not data_service:
        return []
    try:
        return data_service.list_data_elements(limit)
    except Exception as e:
        logger.error(f"Error listing data elements: {e}")
        return []

@mcp.tool()
def delete_data_element(element_id: str) -> bool:
    """
    Deletes a data element from the privacy data governance graph.
    
    Args:
        element_id: The unique identifier of the data element to delete
    
    Returns:
        True if the deletion was successful, False otherwise
    """
    logger.info(f">>> 🛠️ Tool: 'delete_data_element' called with element_id='{element_id}'")
    if not data_service:
        return False
    try:
        return data_service.delete_data_element(element_id)
    except Exception as e:
        logger.error(f"Error deleting data element: {e}")
        return False

@mcp.tool()
def create_relationship(from_entity_id: str, to_entity_id: str, relationship_type: str, properties: Dict[str, Any] = None) -> bool:
    """
    Creates a relationship between two entities in the privacy data governance graph.
    
    Args:
        from_entity_id: ID of the source entity
        to_entity_id: ID of the target entity
        relationship_type: Type of relationship (e.g., "contains", "processes")
        properties: Optional dictionary of additional properties
    
    Returns:
        True if the relationship was created successfully, False otherwise
    """
    logger.info(f">>> 🛠️ Tool: 'create_relationship' called: {from_entity_id} -> {to_entity_id} ({relationship_type})")
    if not data_service:
        return False
    try:
        # Ensure properties is a valid dictionary
        clean_properties = {}
        if properties and isinstance(properties, dict):
            # Convert any non-string keys to strings
            for k, v in properties.items():
                if isinstance(v, (str, int, float, bool)):
                    clean_properties[str(k)] = v
                else:
                    # Convert complex objects to strings
                    clean_properties[str(k)] = str(v)
        elif properties:
            # Handle non-dict properties
            clean_properties["raw_properties"] = str(properties)
            
        # Ensure properties is JSON serializable
        json_properties = None
        if clean_properties:
            try:
                # Convert to JSON string and back to ensure it's serializable
                json_properties = json.dumps(clean_properties)
                json_properties = json.loads(json_properties)
            except (TypeError, ValueError) as e:
                logger.error(f"Properties not JSON serializable: {e}")
                # Fall back to a simple string representation
                json_properties = {"raw_properties": str(clean_properties)}
            
        # Map from_entity_id to source_id and to_entity_id to target_id
        return data_service.create_relationship(
            source_id=from_entity_id,
            target_id=to_entity_id,
            relationship_type=relationship_type,
            properties=json_properties
        )
    except Exception as e:
        logger.error(f"Error creating relationship: {e}")
        return False

@mcp.tool()
def get_relationships(entity_id: str) -> List[Dict[str, Any]]:
    """
    Retrieves relationships for a specific entity.
    
    Args:
        entity_id: The unique identifier of the entity
    
    Returns:
        A list of relationship dictionaries
    """
    logger.info(f">>> 🛠️ Tool: 'get_relationships' called with entity_id='{entity_id}'")
    if not data_service:
        return []
    try:
        return data_service.get_relationships(entity_id)
    except Exception as e:
        logger.error(f"Error getting relationships: {e}")
        return []

@mcp.tool()
def delete_relationship(source_id: str, target_id: str) -> bool:
    """
    Deletes a relationship between two entities in the privacy data governance graph.
    
    Args:
        source_id: ID of the source entity
        target_id: ID of the target entity
    
    Returns:
        True if the relationship was deleted successfully, False otherwise
    """
    logger.info(f">>> 🛠️ Tool: 'delete_relationship' called: {source_id} -> {target_id}")
    if not data_service:
        return False
    try:
        return data_service.delete_relationship(source_id=source_id, target_id=target_id)
    except Exception as e:
        logger.error(f"Error deleting relationship: {e}")
        return False

# For local development, run the FastMCP server directly
if __name__ == "__main__":
    port = int(os.getenv("PORT", 8080))
    logger.info(f"🚀 MCP server started on port {port}")
    asyncio.run(
        mcp.run_async(
            transport="streamable-http",
            host="0.0.0.0",
            port=port,
        )
    )
