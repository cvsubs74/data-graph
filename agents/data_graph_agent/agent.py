# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Agent module for the data graph agent."""

import logging
import warnings
from google.adk.agents import LlmAgent
from .config import Config
from .prompts import GLOBAL_INSTRUCTION, INSTRUCTION
from .tools.tools import mcp_toolset, scrape_and_extract_policy_data
from .shared_libraries.callbacks import (
    before_model_callback,
    before_agent_callback,
    before_tool_callback,
    after_tool_callback
)

warnings.filterwarnings("ignore", category=UserWarning, module=".*pydantic.*")

# Get configuration
configs = Config()

# Configure logging
logger = logging.getLogger(__name__)

def create_agent() -> LlmAgent:
    """Constructs the ADK currency conversion agent."""
    logger.info("--- 🔧 Loading MCP tools from MCP Server... ---")
    logger.info("--- 🤖 Creating ADK Currency Agent... ---")
    return LlmAgent(
        model=configs.agent_settings.model,
        name=configs.agent_settings.name,
        description=GLOBAL_INSTRUCTION,
        instruction=INSTRUCTION,
        tools=[
            mcp_toolset, scrape_and_extract_policy_data
        ],
        before_tool_callback=before_tool_callback,
        after_tool_callback=after_tool_callback,
        before_agent_callback=before_agent_callback,
        before_model_callback=before_model_callback,
    )

root_agent = create_agent()
