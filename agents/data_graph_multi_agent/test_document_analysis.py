#!/usr/bin/env python3
"""Test script for Document Analysis agent."""

import asyncio
import logging
import json
from google.adk.agents import LlmAgent
from config import Config
from tools.tools import document_analysis_toolset
from prompts import DOCUMENT_ANALYSIS_INSTRUCTION
from shared_libraries.callbacks import (
    before_model_callback,
    before_agent_callback,
    before_tool_callback,
    after_tool_callback
)

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Sample privacy policy content for testing
SAMPLE_POLICY = """
Privacy Policy – Privacy & Terms – Google
Privacy & Terms
Overview
Privacy Policy
Introduction
Information Google collects
Why Google collects data
Your privacy controls
Sharing your information
Keeping your information secure
Exporting & deleting your information
Retaining your information
Compliance & cooperation with regulators
About this policy
Related privacy practices
When you use our services, you're trusting us with your information. We understand this is a big responsibility and work hard to protect your information and put you in control.
This Privacy Policy is meant to help you understand what information we collect, why we collect it, and how you can update, manage, export, and delete your information.
"""

async def test_document_analysis():
    """Test the Document Analysis agent directly."""
    configs = Config()
    
    # Create Document Analysis agent
    document_analysis_agent = LlmAgent(
        name="DocumentAnalysisAgent",
        model=configs.agent_settings.model,
        instruction=DOCUMENT_ANALYSIS_INSTRUCTION,
        tools=[document_analysis_toolset],
        before_tool_callback=before_tool_callback,
        after_tool_callback=after_tool_callback,
        before_agent_callback=before_agent_callback,
        before_model_callback=before_model_callback
    )
    
    # Run the agent with sample policy content
    logger.info("Running Document Analysis agent...")
    result = await document_analysis_agent.run(
        {"parsed_policy_content": SAMPLE_POLICY}
    )
    
    # Log the result
    logger.info("Document Analysis agent result:")
    logger.info(json.dumps(result, indent=2))
    
    return result

if __name__ == "__main__":
    asyncio.run(test_document_analysis())
