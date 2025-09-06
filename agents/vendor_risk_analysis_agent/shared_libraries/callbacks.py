"""Callback functions for the data graph agent."""

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
    return None
