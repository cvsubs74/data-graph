"""Callback functions for the vendor risk analysis agent."""

import logging
import json
import time
from datetime import datetime
from typing import Any, Dict, List, Optional
from google.adk.agents.callback_context import CallbackContext
from google.adk.models import LlmResponse, LlmRequest
from google.adk.tools.base_tool import BaseTool
from google.adk.tools.tool_context import ToolContext
from google.genai import types

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("vendor_risk_agent.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("vendor_risk_agent")


def before_model_callback(callback_context: CallbackContext, llm_request: LlmRequest) -> Optional[LlmResponse]:
    """Callback before the model is called.
    
    Args:
        callback_context: The context object containing information about the current request.
        llm_request: The LLM request object.
        
    Returns:
        None if the request should proceed, or a LlmResponse with an error message.
    """
    agent_name = callback_context.agent_name if hasattr(callback_context, 'agent_name') else "unknown"
    logger.info(f"Before model callback called for agent: {agent_name}")
    
    # Add timestamp to state for tracking execution time
    callback_context.state[f"{agent_name}_model_start_time"] = datetime.now().isoformat()
    
    # Log the state
    try:
        state_str = json.dumps({k: str(v) for k, v in dict(callback_context.state).items()}, indent=2)
        logger.debug(f"Model state: {state_str}")
    except Exception as e:
        logger.debug(f"Could not serialize state: {str(e)}")
    
    return None


def before_agent_callback(callback_context: CallbackContext) -> Optional[types.Content]:
    """Callback before the agent is called.
    
    Args:
        callback_context: The callback context.
        
    Returns:
        None if the request should proceed, or a dict with an error message.
    """
    agent_name = callback_context.agent_name if hasattr(callback_context, 'agent_name') else "unknown"
    logger.info(f"Before agent callback called for agent: {agent_name}")
    
    # Add timestamp to state for tracking execution time
    callback_context.state[f"{agent_name}_start_time"] = datetime.now().isoformat()
    
    # Log the state
    try:
        state_str = json.dumps({k: str(v) for k, v in dict(callback_context.state).items()}, indent=2)
        logger.debug(f"Agent state: {state_str}")
    except Exception as e:
        logger.debug(f"Could not serialize state: {str(e)}")
    
    return None


def after_agent_callback(callback_context: CallbackContext) -> Optional[types.Content]:
    """Callback after the agent is called.
    
    Args:
        callback_context: The callback context.
        
    Returns:
        None if the request should proceed, or a dict with an error message.
    """
    agent_name = callback_context.agent_name if hasattr(callback_context, 'agent_name') else "unknown"
    logger.info(f"After agent callback called for agent: {agent_name}")
    
    # Calculate execution time if start time was recorded
    start_time_key = f"{agent_name}_start_time"
    if start_time_key in callback_context.state:
        try:
            start_time = datetime.fromisoformat(callback_context.state[start_time_key])
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            logger.info(f"Agent duration: {agent_name} took {duration:.2f} seconds")
        except Exception as e:
            logger.debug(f"Could not calculate duration: {str(e)}")
    
    # Log the state
    try:
        state_str = json.dumps({k: str(v) for k, v in dict(callback_context.state).items()}, indent=2)
        logger.debug(f"Agent final state: {state_str}")
    except Exception as e:
        logger.debug(f"Could not serialize state: {str(e)}")
    
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
    agent_name = tool_context.agent_name if hasattr(tool_context, 'agent_name') else "unknown"
    logger.info(f"Before tool callback called for {tool_name} by agent {agent_name}")
    
    # Log tool arguments
    try:
        args_str = json.dumps(args, indent=2)
        logger.info(f"Tool arguments: {args_str}")
    except Exception as e:
        logger.info(f"Tool arguments: {str(args)[:500]}... (truncated)")
    
    # Add timestamp to state for tracking execution time
    tool_context.state[f"{tool_name}_start_time"] = datetime.now().isoformat()
    
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
    agent_name = tool_context.agent_name if hasattr(tool_context, 'agent_name') else "unknown"
    logger.info(f"After tool callback called for tool: {tool_name} by agent {agent_name}")
    
    # Log tool response
    try:
        response_str = json.dumps(tool_response, indent=2)
        logger.info(f"Tool response: {response_str}")
    except Exception as e:
        logger.info(f"Tool response: {str(tool_response)[:500]}... (truncated)")
    
    # Calculate execution time if start time was recorded
    start_time_key = f"{tool_name}_start_time"
    if start_time_key in tool_context.state:
        try:
            start_time = datetime.fromisoformat(tool_context.state[start_time_key])
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            logger.info(f"Tool duration: {tool_name} took {duration:.2f} seconds")
        except Exception as e:
            logger.debug(f"Could not calculate duration: {str(e)}")
    
    return None
