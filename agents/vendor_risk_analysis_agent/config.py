"""Configuration module for the vendor risk analysis agent."""

import os
import logging
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import BaseModel, Field

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


class AgentModel(BaseModel):
    """Agent model settings."""
    name: str = Field(default="vendor_risk_analysis_agent")
    model: str = Field(default="gemini-2.5-flash")


class Config(BaseSettings):
    """Configuration settings for the vendor risk analysis agent."""

    model_config = SettingsConfigDict(
        env_file=os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "../.env"
        ),
        env_prefix="",
        case_sensitive=True,
        extra="ignore",  # Allow extra fields in environment variables
    )
    
    # Main agent settings
    agent_settings: AgentModel = Field(default=AgentModel())
    app_name: str = "vendor_risk_analysis_agent"
    MCP_SERVER_URL: str = Field(
        default="https://vendor-risk-mcp-server-79797180773.us-central1.run.app/mcp"
    )
    
    # Coordinator agent settings
    coordinator_settings: AgentModel = Field(
        default=AgentModel(name="vendor_risk_coordinator_agent")
    )
    
    # Initializer agent settings
    initializer_settings: AgentModel = Field(
        default=AgentModel(name="initializer_agent")
    )
    
    # Researcher agent settings
    researcher_settings: AgentModel = Field(
        default=AgentModel(name="researcher_agent")
    )
    
    # Analyst agent settings
    analyst_settings: AgentModel = Field(
        default=AgentModel(name="analyst_agent")
    )
    
    # Verifier agent settings
    verifier_settings: AgentModel = Field(
        default=AgentModel(name="verifier_agent")
    )
    
    # Optional GCP settings
    GCP_PROJECT: str = Field(default="")
    CLOUD_PROJECT: str = Field(default="")
    CLOUD_LOCATION: str = Field(default="us-central1")
    GENAI_USE_VERTEXAI: str = Field(default="1")
    API_KEY: str | None = Field(default=None)
