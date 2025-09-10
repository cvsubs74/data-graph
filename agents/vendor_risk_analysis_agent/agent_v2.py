"""Vendor Risk Analysis Agent V2 using LoopAgent pattern."""

import asyncio
import os
from google.adk.agents import LoopAgent, LlmAgent, BaseAgent, SequentialAgent
from google.genai import types
from google.adk.runners import InMemoryRunner
from google.adk.agents.invocation_context import InvocationContext
from google.adk.tools.tool_context import ToolContext
from typing import AsyncGenerator, Optional, Dict, Any
from google.adk.events import Event, EventActions
from google.adk.tools import google_search
from google.adk.tools.agent_tool import AgentTool
from google.adk.tools.function_tool import FunctionTool

# --- Import tools from the tools class ---
import sys
import os

# Add the parent directory to sys.path to allow imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import the tools from the tools class
from vendor_risk_analysis_agent.tools.tools import validate_url, scrape_and_extract_vendor_data, mcp_toolset
from vendor_risk_analysis_agent.config import Config
from vendor_risk_analysis_agent.callbacks import before_agent_callback, after_agent_callback, before_tool_callback, after_tool_callback

# Get configuration
configs = Config()

# --- State Keys ---
STATE_VENDOR_URL = "vendor_url"
STATE_VENDOR_DATA = "vendor_data"
STATE_RISK_QUESTIONS = "risk_questions"
STATE_RESEARCH_FINDINGS = "research_findings"
STATE_VALIDATED_FINDINGS = "validated_findings"
STATE_FINAL_REPORT = "final_report"
STATE_RESEARCH_CRITICISM = "research_criticism"

# --- Completion Phrase ---
RESEARCH_COMPLETE_PHRASE = "The research is comprehensive and well-supported; no further refinements are needed."

# --- Tool Definition for Loop Exit ---
def exit_research_loop(tool_context: ToolContext):
    """Call this function ONLY when the research critique confirms that the research is complete and no further changes are needed."""
    print(f"  [Tool Call] exit_research_loop triggered by {tool_context.agent_name}")
    tool_context.actions.escalate = True
    return {"status": "Research loop exited successfully."}

# --- Agent Definitions ---

# STEP 1a: URL Validator Agent
url_validator_agent = LlmAgent(
    name="URLValidatorAgent",
    model=configs.agent_settings.model,
    description="Validates a vendor URL",
    instruction="""
    ## Persona
    You are a specialized URL Validator for vendor risk assessments.

    ## Task
    1.  You will receive a vendor URL.
    2.  Use the `validate_url` tool to check if the URL is valid and accessible.
    3.  **If validation fails**, respond with a clear error message: "Error: The provided URL is invalid or inaccessible. Please provide a valid URL."
    4.  **If validation succeeds**, respond with: "URL validation successful. The URL is valid and accessible."
    5.  Do not perform any additional actions beyond validation.
    """,
    tools=[validate_url],
    output_key="validation_result",
    before_tool_callback=before_tool_callback,
    after_tool_callback=after_tool_callback,
    before_agent_callback=before_agent_callback,
    after_agent_callback=after_agent_callback,
)

# STEP 1b: Content Scraper Agent
content_scraper_agent = LlmAgent(
    name="ContentScraperAgent",
    model=configs.agent_settings.model,
    description="Scrapes and extracts vendor data from a validated URL",
    instruction="""
    ## Persona
    You are a specialized Content Scraper for vendor risk assessments.

    ## Task
    1.  You will receive a validated vendor URL.
    2.  Use the `scrape_and_extract_vendor_data` tool to extract data from the website.
    3.  **If scraping fails**, respond with: "Error: I was unable to extract data from the website."
    4.  **If scraping succeeds**, output **ONLY** a concise summary of the vendor data, including:
        - Company name
        - Industry
        - Products/services
        - Key security/compliance information if available
        - Any other relevant information for vendor risk assessment
    """,
    tools=[scrape_and_extract_vendor_data],
    output_key=STATE_VENDOR_DATA,
    before_tool_callback=before_tool_callback,
    after_tool_callback=after_tool_callback,
    before_agent_callback=before_agent_callback,
    after_agent_callback=after_agent_callback,
)

url_validator_tool = AgentTool(
    agent=url_validator_agent,
    skip_summarization=False
)

content_scraper_tool = AgentTool(
    agent=content_scraper_agent,
    skip_summarization=False
)

# STEP 2: Risk Question Generator Agent
question_generator_agent = LlmAgent(
    name="QuestionGeneratorAgent",
    model=configs.agent_settings.model,
    description="Generates tailored risk assessment questions based on vendor profile",
    instruction="""
    ## Persona
    You are a senior risk analyst specializing in creating due diligence questionnaires.

    ## Context
    You have been provided with initial data about a vendor:
    ```json
    {vendor_data}
    ```

    ## Task
    Your task is to generate a tailored and comprehensive list of risk assessment questions.
    1.  First, call the `get_risk_questions` function from the MCP toolset to get a baseline set of questions relevant to the vendor's industry.
    2.  Then, enhance and customize this list by adding specific questions based on the vendor's profile (services, products, etc.).
    3.  Focus on key risk domains: Security, Data Privacy, Compliance, Business Continuity, and Governance.

    ## Output Requirement
    Output **ONLY** a numbered list of the final questions grouped by category.
    """,
    tools=[mcp_toolset],
    output_key=STATE_RISK_QUESTIONS,
    before_tool_callback=before_tool_callback,
    after_tool_callback=after_tool_callback,
    before_agent_callback=before_agent_callback,
    after_agent_callback=after_agent_callback,
)

# STEP 3: Researcher Agent
researcher_agent = LlmAgent(
    name="ResearcherAgent",
    model=configs.agent_settings.model,
    description="Conducts initial research to answer vendor risk assessment questions",
    instruction="""
    ## Persona
    You are a skilled Research Analyst executing the first pass of a research assignment.

    ## Context
    - **Vendor Data:** `{vendor_data}`
    - **Risk Questions:** `{risk_questions}`

    ## Task
    Conduct initial research to answer each risk question.
    1.  For each question, use the `google_search` tool to find relevant, high-quality sources.
    2.  Synthesize the information from sources to form a concise answer.
    3.  Provide brief, logical reasoning for your answer, supported by inline citations `[n]`.
    4.  Compile all sources into a consolidated `References` section at the end.

    ## Output Format
    Answer all questions first, then add the references list at the very end.
    ```
    **Question**: [Original question text]
    **Answer**: [Your synthesized answer]
    **Reasoning**: [Brief explanation with inline citations like [1] and [2].]
    ---
    **(Repeat for all questions)**
    ---
    **References**:
    [1] Source Title: [https://exact-url-from-search.com/page](https://exact-url-from-search.com/page)
    [2] Another Source: [https://another-url.com/article](https://another-url.com/article)
    ```

    ## Critical Sourcing Rules
    - Every reference **MUST** include both a title and a complete, unmodified URL.
    - **ONLY** use URLs that appear directly in the search tool results.
    - **NEVER** include URLs containing 'vertexai' or similar internal AI-related domains.
    """,
    tools=[google_search],
    output_key=STATE_RESEARCH_FINDINGS,
    before_tool_callback=before_tool_callback,
    after_tool_callback=after_tool_callback,
    before_agent_callback=before_agent_callback,
    after_agent_callback=after_agent_callback,
)

# STEP 4: Report Generator Agent
report_generator_agent = LlmAgent(
    name="ReportGeneratorAgent",
    model=configs.agent_settings.model,
    description="Creates a comprehensive, professional vendor risk assessment report",
    include_contents='none',
    instruction="""
    ## Persona
    You are an executive communications specialist tasked with creating a final vendor risk report. Your audience is business leadership, so clarity and professionalism are paramount.
    
    ## URL Validation Process
    Before finalizing the report, you must validate all URLs in the references:
    1. Extract all URLs from the research findings references section
    2. For each URL, use the `validate_url_agent` tool to check if it's accessible
    3. Only include URLs that are successfully validated
    4. Mark each validated URL with a checkmark (✓) in the final references section
    5. If any URLs fail validation, note this at the end of the references section

    ## Context
    - **Vendor Profile:** `{vendor_data}`
    - **Audited Research Findings:** `{research_findings}`

    ## Task
    Synthesize all provided information into a polished, professional risk assessment report. The report must be objective, well-structured, and easy to understand.

    ## Final Report Structure
    Use the following markdown format precisely.

    # Vendor Risk Assessment Report: [Vendor Name from Vendor Profile]

    ## 1. Executive Summary
    (A brief, high-level overview of the vendor, key findings, and a final, clear recommendation.)

    ## 2. Vendor Profile
    (Present the information from the research findings in a clean, readable format.)

    ## 3. Detailed Risk Assessment
    (Present the final, audited question-and-answer section from research findings. Do not include the 'Reasoning' fields, only the Questions and Answers.)

    ## 4. Recommendations
    (Provide specific, actionable recommendations based on the findings. For example, "Request SOC 2 Type II report from the vendor before proceeding.")

    ## 5. References
    (Validate all URLs from the research findings using the url_validator_tool and include only valid references in this section. Mark each validated reference with a checkmark (✓) to indicate it has been verified as accessible.)
    """,
    tools=[url_validator_tool],
    output_key=STATE_FINAL_REPORT,
    before_agent_callback=before_agent_callback,
    after_agent_callback=after_agent_callback,
)

# --- Wrap Agents as Tools ---
# Create agent tools using AgentTool to wrap the existing agent
risk_questions_tool = AgentTool(
    agent=question_generator_agent,
    skip_summarization=False
)

research_tool = AgentTool(
    agent=researcher_agent,
    skip_summarization=False
)

report_tool = AgentTool(
    agent=report_generator_agent,
    skip_summarization=False
)

# --- Main Orchestrator Agent ---
root_agent = LlmAgent(
    name="VendorRiskAnalysisOrchestrator",
    model=configs.agent_settings.model,
    include_contents='default',
    before_agent_callback=before_agent_callback,
    after_agent_callback=after_agent_callback,
    instruction="""
    ## Persona
    You are a helpful and methodical project manager for vendor risk assessments. Your job is to guide the user through a comprehensive vendor risk analysis process.

    ## Workflow
    You must guide the user through the process step-by-step, using your tools in a precise order. **Never** proceed to the next step without explicit user confirmation.

    1.  **Introduction & URL Validation (Step 1a)**
        - Start by greeting the user and explaining your purpose.
        - Ask the user to provide the vendor's URL.
        - Use the `validate_url_agent` tool to validate the URL.
        - If validation fails, ask the user to provide a valid URL.
        - **Confirm**: Ask the user, "I've validated the vendor's URL. Shall I proceed with content extraction?"

    2.  **Content Extraction (Step 1b)**
        - After user confirmation, use the `scrape_content_agent` tool to extract data from the validated URL.
        - Present the extracted vendor data to the user.
        - **Confirm**: Ask the user, "I've extracted the vendor data. Shall I proceed with generating risk assessment questions?"

    3.  **Risk Question Generation (Step 2)**
        - After user confirmation, use the `generate_risk_questions` tool to generate targeted risk assessment questions.
        - Present the questions to the user.
        - **Confirm**: Ask the user, "Here are the proposed risk questions. Shall I proceed with the research phase?"

    4.  **Comprehensive Research (Step 3)**
        - After user confirmation, use the `research_vendor` tool. Inform the user this may take some time.
        - Present the research findings to the user.
        - **Confirm**: Ask the user, "The research is complete. Shall I proceed with generating the final report?"

    5.  **Final Report (Step 4)**
        - After user confirmation, use the `generate_report` tool.
        - Present the complete, final report to the user.
        - Conclude the process by asking if the user has any further questions.
    """,
    tools=[url_validator_tool, content_scraper_tool, risk_questions_tool, research_tool, report_tool],
    description="Orchestrates a comprehensive vendor risk analysis by using specialized tools."
)