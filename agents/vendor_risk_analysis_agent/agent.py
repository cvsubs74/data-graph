"""Agent module for the vendor risk analysis agent."""

import logging
import warnings
from google.adk.agents import LlmAgent, SequentialAgent
from google.adk.tools import google_search

from .config import Config
from .prompts import GLOBAL_INSTRUCTION
from .tools.tools import mcp_toolset, scrape_and_extract_vendor_data
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

# 1. URL Validator Agent - Validates the vendor URL and ensures it contains the vendor name
url_validator_agent = LlmAgent(
    name="URLValidatorAgent",
    model=configs.agent_settings.model,
    instruction="""Validate the vendor URL and ensure it's legitimate.
    
    1. Scrape the website content using the scrape_and_extract_vendor_data tool
    2. Verify that the website is valid and operational
    3. Check if the vendor name appears in the URL or website content
    4. Extract basic information about the vendor
    5. Output a structured summary with:
       - Vendor name
       - Vendor URL
       - URL validation status (valid/invalid)
       - Brief description of vendor's business
    """,
    tools=[scrape_and_extract_vendor_data],
    output_key="url_validation_result",
    before_tool_callback=before_tool_callback,
    after_tool_callback=after_tool_callback,
    before_agent_callback=before_agent_callback,
    before_model_callback=before_model_callback,
)

# 2. Risk Questions Identifier Agent - Uses MCP toolset to get risk questions
risk_questions_agent = LlmAgent(
    name="RiskQuestionsAgent",
    model=configs.agent_settings.model,
    instruction="""Retrieve all pre-defined risk assessment questions from the MCP server.
    
    1. Use the MCP toolset to retrieve ALL risk questions using the get_risk_questions tool
       - Do NOT pass any category parameter - get all questions
       - Do NOT create any new risk questions - only use the pre-defined ones from the MCP server
    2. Organize the retrieved questions in a clear, structured format
    3. Output the complete list of risk questions that will be used by the researcher agent
    
    IMPORTANT: 
    - Do NOT create or generate any new risk questions
    - Only use the exact questions retrieved from the MCP server
    - If no questions are returned, report this issue but do not create substitute questions
    
    Your output should include:
    - The complete list of risk questions retrieved from the MCP server
    - A note confirming that these are the exact questions from the MCP server
    """,
    tools=[mcp_toolset],
    output_key="risk_questions",
    before_tool_callback=before_tool_callback,
    after_tool_callback=after_tool_callback,
    before_agent_callback=before_agent_callback,
    before_model_callback=before_model_callback,
)

# 3. Researcher Agent - Answers risk questions using Google search
researcher_agent = LlmAgent(
    name="ResearcherAgent",
    model=configs.agent_settings.model,
    instruction="""Conduct comprehensive research on the vendor and answer ONLY the risk questions provided by the MCP server.
    
    1. Review the vendor information from the URL validator agent
    2. Use the EXACT risk questions provided by the risk questions agent
    3. Use Google search to gather detailed information about the vendor
    4. Answer ONLY the risk questions provided by the MCP server
    5. For each question, provide:
       - The original question exactly as provided by the MCP server
       - A detailed answer based on research
       - Sources/references for the information
    6. Include a comprehensive vendor profile with all relevant information
    
    IMPORTANT:
    - Do NOT create any new risk questions
    - Only answer the exact questions provided by the MCP server
    - If a question cannot be answered with available information, state this clearly
    
    Your output should contain:
    - Complete vendor profile
    - All MCP risk questions with detailed answers
    - Sources for each piece of information
    """,
    tools=[google_search],
    output_key="research_results",
    before_tool_callback=before_tool_callback,
    after_tool_callback=after_tool_callback,
    before_agent_callback=before_agent_callback,
    before_model_callback=before_model_callback,
)

# 4. Verification Agent - Verifies all information using Google search
verification_agent = LlmAgent(
    name="VerificationAgent",
    model=configs.agent_settings.model,
    instruction="""Verify the research results and create a final report with answers to the MCP risk questions.
    
    1. Review the research results from the previous agent
    2. Use Google search to verify key facts and claims about the vendor
    3. Verify the answers to the MCP risk questions
    4. Do NOT add any new risk questions that weren't in the original MCP list
    5. Check for any inconsistencies or inaccuracies in the research
    6. Generate a final comprehensive vendor risk assessment report with:
       - Executive Summary
       - Vendor Profile
       - Risk Assessment Methodology
       - Risk Assessment Results
       - FAQ section with verified answers to ONLY the original MCP risk questions
       - Recommendations
       - Verification Statement
    
    IMPORTANT:
    - Only include the risk questions that came from the MCP server
    - Do NOT create any new risk questions
    - Maintain the exact wording of the original MCP questions
    - If any answers are insufficient, improve them with additional research
    """,
    tools=[google_search],
    output_key="final_report",
    before_tool_callback=before_tool_callback,
    after_tool_callback=after_tool_callback,
    before_agent_callback=before_agent_callback,
    before_model_callback=before_model_callback,
)

# Define the main workflow using a SequentialAgent
# This agent orchestrates the four specialized agents in sequence
root_agent = SequentialAgent(
    name="VendorRiskCoordinator",
    sub_agents=[
        url_validator_agent,
        risk_questions_agent,
        researcher_agent,
        verification_agent
    ],
    description=GLOBAL_INSTRUCTION
)
