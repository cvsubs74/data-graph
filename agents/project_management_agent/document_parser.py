"""Document parser agent for the project management system."""

import logging
from typing import Dict, Any, List, Optional
from google.adk.agents import LlmAgent
from google.adk.tools.agent_tool import AgentTool
from google.adk.tools.tool_context import ToolContext

from .config import Config
from .prompts import GLOBAL_INSTRUCTION, DOCUMENT_PARSER_INSTRUCTION
from .tools.tools import parse_document

# Configure logging
logger = logging.getLogger(__name__)
logging.basicConfig(format="[%(levelname)s]: %(message)s", level=logging.INFO)

# Get configuration
configs = Config()

# Import types for schemas and config
from google.genai import types
from pydantic import BaseModel, Field

# Define input and output schemas
class DocumentParserInput(BaseModel):
    """Input schema for document parser agent."""
    document_content: str = Field(description="Raw content of the document to parse")

class DocumentParserOutput(BaseModel):
    """Output schema for document parser agent."""
    parsed_content: str = Field(description="Parsed content of the document")
    status: str = Field(description="Status of the parsing operation")

# Create the document parser agent
document_parser_agent = LlmAgent(
    name="DocumentParserAgent",
    description="Parses uploaded documents and extracts their content and structure",
    model=configs.agent_settings.model,
    instruction=GLOBAL_INSTRUCTION + "\n\n" + DOCUMENT_PARSER_INSTRUCTION,
    tools=[parse_document],
    generate_content_config=types.GenerateContentConfig(
        temperature=configs.agent_settings.temperature,
        top_p=configs.agent_settings.top_p,
        top_k=configs.agent_settings.top_k,
        max_output_tokens=configs.agent_settings.max_output_tokens
    )
)

# We no longer need the AgentTool wrapper since we're using sub-agents pattern
# We also don't need the helper functions since we're using structured input/output
