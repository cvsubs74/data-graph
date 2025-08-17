"""Configuration module for the data graph agent."""

import os
import logging
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import BaseModel, Field

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


class AgentModel(BaseModel):
    """Agent model settings."""

    name: str = Field(default="data_graph_agent")
    model: str = Field(default="gemini-2.5-flash-lite")


class Config(BaseSettings):
    """Configuration settings for the data graph agent."""

    model_config = SettingsConfigDict(
        env_file=os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "../.env"
        ),
        env_prefix="",
        case_sensitive=True,
        extra="ignore",  # Allow extra fields in environment variables
    )
    agent_settings: AgentModel = Field(default=AgentModel())
    app_name: str = "data_graph_agent"
    MCP_SERVER_URL: str = Field(
        default="https://mcp-server-79797180773.us-central1.run.app/mcp"
    )
    # Optional GCP settings
    GCP_PROJECT: str = Field(default="")
    CLOUD_PROJECT: str = Field(default="")
    CLOUD_LOCATION: str = Field(default="us-central1")
    GENAI_USE_VERTEXAI: str = Field(default="1")
    API_KEY: str | None = Field(default=None)


