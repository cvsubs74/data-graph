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

"""Agent module for the data graph multi agent."""

import logging
import warnings
from google.adk.agents import LlmAgent, SequentialAgent
from .config import Config
from .tools.tools import scrape_and_extract_policy_data, build_data_graph, mcp_toolset
from .shared_libraries.callbacks import (
    before_model_callback,
    before_agent_callback,
    before_tool_callback,
    after_tool_callback
)
from .prompts import GLOBAL_INSTRUCTION, DOCUMENT_ANALYSIS_INSTRUCTION, GRAPH_CONSTRUCTION_INSTRUCTION

warnings.filterwarnings("ignore", category=UserWarning, module=".*pydantic.*")

# Get configuration
configs = Config()

# Configure logging
logger = logging.getLogger(__name__)

# 1. Define the agent responsible for parsing the document.
document_analysis_agent = LlmAgent(
    name="DocumentAnalysisAgent",
    model=configs.agent_settings.model,
    instruction=DOCUMENT_ANALYSIS_INSTRUCTION,
    tools=[scrape_and_extract_policy_data, mcp_toolset],
    # This key saves the agent's final output to the session state,
    # making it available for the next agent in the sequence.
    output_key="policy_analysis_result",
    # Add callbacks directly as parameters
    before_tool_callback=before_tool_callback,
    after_tool_callback=after_tool_callback,
    before_agent_callback=before_agent_callback,
    before_model_callback=before_model_callback
)

# 2. Define the agent responsible for building the data graph.
graph_construction_agent = LlmAgent(
    name="GraphConstructionAgent",
    model=configs.agent_settings.model,
    instruction=GRAPH_CONSTRUCTION_INSTRUCTION,
    tools=[build_data_graph, mcp_toolset],
    # Add callbacks directly as parameters
    before_tool_callback=before_tool_callback,
    after_tool_callback=after_tool_callback,
    before_agent_callback=before_agent_callback,
    before_model_callback=before_model_callback
)

# 3. Define the main workflow using a SequentialAgent.
# This agent orchestrates the sub-agents in a fixed order.
root_agent = SequentialAgent(
    name="DataGraphWorkflow",
    sub_agents=[document_analysis_agent, graph_construction_agent],
    description=GLOBAL_INSTRUCTION
)
