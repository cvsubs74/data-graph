"""Project analyzer agent for the project management system."""

import logging
from typing import Dict, Any, List, Optional
from google.adk.agents import LlmAgent
from google.adk.tools.agent_tool import AgentTool
from google.adk.tools.tool_context import ToolContext

from .config import Config
from .prompts import GLOBAL_INSTRUCTION, PROJECT_ANALYZER_INSTRUCTION
from .tools import mcp_toolset

# Configure logging
logger = logging.getLogger(__name__)
logging.basicConfig(format="[%(levelname)s]: %(message)s", level=logging.INFO)

# Get configuration
configs = Config()

# Import types for schemas and config
from google.genai import types
from pydantic import BaseModel, Field
from typing import List, Dict

# Define input and output schemas
class Risk(BaseModel):
    """Risk identified in the project."""
    name: str = Field(description="Name of the risk")
    level: str = Field(description="Risk level (High, Medium, Low)")
    description: str = Field(description="Description of the risk")
    mitigation: str = Field(description="Mitigation strategy")

class Recommendation(BaseModel):
    """Recommendation for the project."""
    title: str = Field(description="Title of the recommendation")
    description: str = Field(description="Description of the recommendation")
    priority: str = Field(description="Priority level (High, Medium, Low)")

class ProjectAnalyzerInput(BaseModel):
    """Input schema for project analyzer agent."""
    entity_detection_result: Dict[str, Any] = Field(description="Result from entity detection")
    project_context: Optional[str] = Field(None, description="Additional project context")

class ProjectAnalyzerOutput(BaseModel):
    """Output schema for project analyzer agent."""
    document_url: str = Field(description="URL of the document")
    project_summary: str = Field(description="Summary of the project analysis")
    identified_risks: List[Risk] = Field(description="List of identified risks")
    recommendations: List[Recommendation] = Field(description="List of recommendations")
    status: str = Field(description="Status of the project analysis operation")

# Create the project analyzer agent
project_analyzer_agent = LlmAgent(
    name="ProjectAnalyzerAgent",
    description="Analyzes projects based on detected entities and provides risk assessment and recommendations",
    model=configs.agent_settings.model,
    instruction=GLOBAL_INSTRUCTION + "\n\n" + PROJECT_ANALYZER_INSTRUCTION,
    tools=[mcp_toolset],
    generate_content_config=types.GenerateContentConfig(
        temperature=configs.agent_settings.temperature,
        top_p=configs.agent_settings.top_p,
        top_k=configs.agent_settings.top_k,
        max_output_tokens=configs.agent_settings.max_output_tokens
    )
)

# We no longer need the AgentTool wrapper since we're using sub-agents pattern
# We also don't need the helper functions since we're using structured input/output
