"""Entity detector agent for the project management system."""

import logging
from typing import Dict, Any, List, Optional
from google.adk.agents import LlmAgent
from google.adk.tools.agent_tool import AgentTool
from google.adk.tools.tool_context import ToolContext

from .config import Config
from .prompts import GLOBAL_INSTRUCTION, ENTITY_DETECTOR_INSTRUCTION
from .tools.tools import metadata_mcp_toolset

# Configure logging
logger = logging.getLogger(__name__)
logging.basicConfig(format="[%(levelname)s]: %(message)s", level=logging.INFO)

# Get configuration
configs = Config()

# Import types for schemas and config
from google.genai import types
from pydantic import BaseModel, Field
from typing import List

# Define input and output schemas
class Entity(BaseModel):
    """Entity detected in a document."""
    name: str = Field(description="Name of the entity")
    type: str = Field(description="Type of the entity")
    description: Optional[str] = Field(None, description="Description of the entity")

class EntityDetectorInput(BaseModel):
    """Input schema for entity detector agent."""
    document_parsing_result: Dict[str, Any] = Field(description="Result from document parsing")

class EntityDetectorOutput(BaseModel):
    """Output schema for entity detector agent."""
    document_url: str = Field(description="URL of the document")
    detected_entities: List[Entity] = Field(description="List of detected entities")
    status: str = Field(description="Status of the entity detection operation")

# Create the entity detector agent
entity_detector_agent = LlmAgent(
    name="EntityDetectorAgent",
    description="Detects and classifies entities in parsed documents",
    model=configs.agent_settings.model,
    instruction=GLOBAL_INSTRUCTION + "\n\n" + ENTITY_DETECTOR_INSTRUCTION,
    tools=[metadata_mcp_toolset],
    generate_content_config=types.GenerateContentConfig(
        temperature=configs.agent_settings.temperature,
        top_p=configs.agent_settings.top_p,
        top_k=configs.agent_settings.top_k,
        max_output_tokens=configs.agent_settings.max_output_tokens
    )
)

# We no longer need the AgentTool wrapper since we're using sub-agents pattern
# We also don't need the helper functions since we're using structured input/output
