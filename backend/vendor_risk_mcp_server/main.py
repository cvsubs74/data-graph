import asyncio
import json
import logging
import os
from typing import List, Dict, Any, Optional

from fastmcp import FastMCP

# Import our vendor risk service
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from services.vendor_risk_service import VendorRiskService

logger = logging.getLogger(__name__)
logging.basicConfig(format="[%(levelname)s]: %(message)s", level=logging.INFO)

mcp = FastMCP("Vendor Risk Analysis MCP Server")

# Initialize vendor risk service
try:
    vendor_risk_service = VendorRiskService()
    logger.info("VendorRiskService initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize VendorRiskService: {e}")
    vendor_risk_service = None

@mcp.tool()
def get_risk_questions() -> List[Dict[str, Any]]:
    """
    Retrieves all risk assessment questions.
    
    Returns:
        A list of question dictionaries with question_id, question_text, question_type, etc.
    """
    logger.info(">>> 🛠️ Tool: 'get_risk_questions' called")
    if not vendor_risk_service:
        return []
    
    try:
        return vendor_risk_service.get_risk_questions()
    except Exception as e:
        logger.error(f"Error getting risk questions: {e}")
        return []

@mcp.tool()
def create_risk_question(question_text: str, question_type: str, category: str, 
                       is_required: bool = True, options: List[Dict[str, str]] = None) -> str:
    """
    Creates a new risk assessment question.
    
    Args:
        question_text: The text of the question
        question_type: The type of question (yes_no, free_text, single_select)
        category: The category the question belongs to
        is_required: Whether the question is required
        options: List of option dictionaries for single_select questions
        
    Returns:
        The unique question_id of the created question
    """
    logger.info(f">>> 🛠️ Tool: 'create_risk_question' called with text='{question_text}'")
    if not vendor_risk_service:
        return ""
    
    try:
        return vendor_risk_service.create_risk_question(
            question_text=question_text,
            question_type=question_type,
            category=category,
            is_required=is_required,
            options=options
        )
    except Exception as e:
        logger.error(f"Error creating risk question: {e}")
        return ""

@mcp.tool()
def update_risk_question(question_id: str, question_text: str = None, 
                       question_type: str = None, category: str = None,
                       is_required: bool = None, options: List[Dict[str, str]] = None) -> bool:
    """
    Updates an existing risk assessment question.
    
    Args:
        question_id: The unique identifier of the question to update
        question_text: Optional new text for the question
        question_type: Optional new type for the question
        category: Optional new category for the question
        is_required: Optional new required flag for the question
        options: Optional new options for single_select questions
        
    Returns:
        True if the update was successful, False otherwise
    """
    logger.info(f">>> 🛠️ Tool: 'update_risk_question' called with question_id='{question_id}'")
    if not vendor_risk_service:
        return False
    
    try:
        return vendor_risk_service.update_risk_question(
            question_id=question_id,
            question_text=question_text,
            question_type=question_type,
            category=category,
            is_required=is_required,
            options=options
        )
    except Exception as e:
        logger.error(f"Error updating risk question: {e}")
        return False

@mcp.tool()
def delete_risk_question(question_id: str) -> bool:
    """
    Deletes a risk assessment question and its options.
    
    Args:
        question_id: The unique identifier of the question to delete
        
    Returns:
        True if the deletion was successful, False otherwise
    """
    logger.info(f">>> 🛠️ Tool: 'delete_risk_question' called with question_id='{question_id}'")
    if not vendor_risk_service:
        return False
    
    try:
        return vendor_risk_service.delete_risk_question(question_id)
    except Exception as e:
        logger.error(f"Error deleting risk question: {e}")
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
