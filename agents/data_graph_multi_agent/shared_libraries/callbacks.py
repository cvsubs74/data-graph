"""Callback functions for the data graph multi agent."""

import logging
from typing import Any, Dict, List, Optional
from google.adk.agents.callback_context import CallbackContext
from google.adk.models import LlmResponse, LlmRequest
from google.adk.tools.base_tool import BaseTool
from google.adk.tools.tool_context import ToolContext
from google.genai import types 
logger = logging.getLogger(__name__)


def before_model_callback(callback_context: CallbackContext, llm_request: LlmRequest) -> Optional[LlmResponse]:
    """Callback before the model is called.
    
    Args:
        callback_context: The context object containing information about the current request.
        
    Returns:
        None if the request should proceed, or a dict with an error message.
    """
    logger.info("Before model callback called")
    return None


def before_agent_callback(callback_context: CallbackContext) -> Optional[types.Content]:
    """Callback before the agent is called.
    
    Args:
        callback_context: The callback context.
        
    Returns:
        None if the request should proceed, or a dict with an error message.
    """
    logger.info("Before agent callback called")
    
    # Get the current agent name
    agent_name = callback_context.agent_name if hasattr(callback_context, 'agent_name') else "Unknown Agent"
    
    # Check if this is a sub-agent in a sequence (not the root agent)
    if agent_name != "DataGraphWorkflow" and hasattr(callback_context, 'session_state'):
        # Get the previous agent's output if available
        session_state = callback_context.session_state
        previous_output = None
        
        # Check if we're moving from Document Analysis to Graph Construction
        if agent_name == "GraphConstructionAgent" and "policy_analysis_result" in session_state:
            previous_output = session_state.get("policy_analysis_result")
            
            # Ask for user confirmation before proceeding
            user_message = f"\n\nThe Document Analysis Agent has completed its work. "
            user_message += f"Would you like to proceed with the Graph Construction Agent? "
            user_message += f"Please confirm by responding with 'Yes' or provide feedback if you'd like changes."
            
            # Return the message to pause execution and wait for user input
            return types.Content(parts=[types.Part.from_text(user_message)])
    
    return None


def before_tool_callback(tool: BaseTool, args: Dict[str, Any], tool_context: ToolContext) -> Optional[Dict]:
    """Callback before a tool is called.

    Args:
        tool: The tool being called.
        args: The arguments passed to the tool.
        tool_context: The tool context.

    Returns:
        None if the request should proceed, or a dict with an error message.
    """
    tool_name = tool.name
    logger.info(f"Before tool callback called for {tool_name}")
    return None


def after_tool_callback(tool: BaseTool, args: Dict[str, Any], tool_context: ToolContext, tool_response: Dict) -> Optional[Dict]:
    """Callback after a tool is called.
    
    Args:
        tool: The tool being called.
        args: The arguments passed to the tool.
        tool_context: The tool context.
        tool_response: The response from the tool.
        
    Returns:
        None if the request should proceed, or a dict with an error message.
    """
    tool_name = tool.name
    logger.info(f"After tool callback called for tool: {tool_name}")
    
    # List of tools that require user confirmation after execution
    important_tools = [
        "scrape_and_extract_policy_data",
        "find_similar_entities",
        "get_similar_entities",
        "visualize_graph_data"
    ]
    
    # Check if this is an important tool that requires user confirmation
    if tool_name in important_tools:
        # Create a user-friendly message based on the tool
        if tool_name == "scrape_and_extract_policy_data":
            user_message = "\n\nI've retrieved and parsed the document content. "
            user_message += "Would you like me to proceed with analyzing this content? "
            user_message += "Please confirm by responding with 'Yes' or provide feedback if you'd like changes."
            
            return {"user_message": user_message}
            
        elif tool_name in ["find_similar_entities", "get_similar_entities"]:
            # Only ask for confirmation if similarity is >= 0.3 (as per updated prompt)
            if tool_response and "similarity" in tool_response and tool_response["similarity"] >= 0.3:
                user_message = "\n\nI've found similar entities in the system. "
                user_message += "Would you like me to proceed with the suggested actions? "
                user_message += "Please confirm by responding with 'Yes' or provide feedback if you'd like changes."
                
                return {"user_message": user_message}
                
        elif tool_name == "visualize_graph_data":
            user_message = "\n\nI've created a visualization of the data graph. "
            user_message += "Would you like me to proceed with the next steps? "
            user_message += "Please confirm by responding with 'Yes' or provide feedback if you'd like changes."
            
            return {"user_message": user_message}
    
    return None
