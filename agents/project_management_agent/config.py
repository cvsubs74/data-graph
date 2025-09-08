"""Configuration module for the project management agent."""

import os
import logging
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import BaseModel, Field

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


class AgentModel(BaseModel):
    """Agent model settings."""

    name: str = Field(default="project_management_agent")
    model: str = Field(default="gemini-2.5-flash")
    temperature: float = Field(default=0.2)
    top_p: float = Field(default=0.95)
    top_k: int = Field(default=40)
    max_output_tokens: int = Field(default=8192)


class Config(BaseSettings):
    """Configuration settings for the project management agent."""

    model_config = SettingsConfigDict(
        env_file=os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "../.env"
        ),
        env_prefix="",
        case_sensitive=True,
        extra="ignore",  # Allow extra fields in environment variables
    )
    agent_settings: AgentModel = Field(default=AgentModel())
    app_name: str = "project_management_agent"
    MCP_SERVER_URL: str = Field(
        default="https://mcp-server-79797180773.us-central1.run.app/mcp"
    )
    # Optional GCP settings
    GCP_PROJECT: str = Field(default="")
    CLOUD_PROJECT: str = Field(default="")
    CLOUD_LOCATION: str = Field(default="us-central1")
    GENAI_USE_VERTEXAI: str = Field(default="1")
    API_KEY: str | None = Field(default=None)
    
    # Logging configuration
    LOG_LEVEL: str = Field(default="INFO")
    
    # Document processing settings
    MAX_DOCUMENT_SIZE: int = Field(default=1000000)  # 1MB
    SUPPORTED_DOCUMENT_TYPES: list[str] = Field(default=["pdf", "docx", "txt", "html"])
    
    # Entity detection settings
    MIN_ENTITY_CONFIDENCE: float = Field(default=0.7)
    MAX_ENTITIES_PER_DOCUMENT: int = Field(default=100)
