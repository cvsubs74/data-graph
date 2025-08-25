#!/usr/bin/env python3
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

"""Test script for the data graph multi agent."""

import logging
import argparse
from google.adk.run import run_agent
from google.adk.state import State

from agents.data_graph_multi_agent import root_agent

# Configure logging
logging.basicConfig(level=logging.INFO, format="[%(levelname)s]: %(message)s")
logger = logging.getLogger(__name__)


def main():
    """Run the data graph multi agent with a test privacy policy URL."""
    parser = argparse.ArgumentParser(description="Test the data graph multi agent")
    parser.add_argument(
        "--url",
        type=str,
        default="https://policies.google.com/privacy",
        help="URL of the privacy policy to analyze",
    )
    args = parser.parse_args()

    # Create initial state with the privacy policy URL
    initial_state = State()
    initial_state.user_input = f"Please analyze the privacy policy at {args.url}"

    # Run the agent
    logger.info(f"Starting analysis of privacy policy at: {args.url}")
    final_state = run_agent(root_agent, initial_state)

    # Print the final response
    logger.info("Analysis complete. Final response:")
    print(final_state.agent_response)


if __name__ == "__main__":
    main()
