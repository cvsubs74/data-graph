"""Project management agent using multi-agent system with Coordinator/Dispatcher pattern."""

import logging
from typing import Dict, Any, List, Optional

from google.adk.agents import LlmAgent
from google.genai import types

from .config import Config
from .prompts import GLOBAL_INSTRUCTION, COORDINATOR_INSTRUCTION
from .document_parser import document_parser_agent
from .entity_detector import entity_detector_agent
from .project_analyzer import project_analyzer_agent

# Configure logging
logger = logging.getLogger(__name__)

# Get configuration
configs = Config()

# --- Multi-Agent System with Coordinator/Dispatcher Pattern ---

# Create the coordinator agent
coordinator_agent = LlmAgent(
    name="ProjectManagementCoordinator",
    model=configs.agent_settings.model,
    instruction=GLOBAL_INSTRUCTION + "\n\n" + COORDINATOR_INSTRUCTION,
    description="Main coordinator for the project management system. Routes requests to specialized agents.",
    # Define sub-agents for the coordinator
    sub_agents=[
        document_parser_agent,
        entity_detector_agent,
        project_analyzer_agent
    ],
    # Configure LLM generation parameters
    generate_content_config=types.GenerateContentConfig(
        temperature=configs.agent_settings.temperature,
        top_p=configs.agent_settings.top_p,
        top_k=configs.agent_settings.top_k,
        max_output_tokens=configs.agent_settings.max_output_tokens
    ),
)

# This is the agent that will be used by the main.py file
root_agent = coordinator_agent
