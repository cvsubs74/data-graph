"""Simplified vendor risk analysis agent using agent-as-tool pattern."""

import logging
from typing import Dict, List, Any, Optional, AsyncGenerator

from google.adk.agents import LlmAgent, BaseAgent
from google.adk.tools import google_search
from google.adk.tools.agent_tool import AgentTool
from google.adk.events import Event
from google.adk.agents import InvocationContext
from google.genai import types

from .config import Config
from .tools.tools import scrape_and_extract_vendor_data, validate_url, mcp_toolset

# Configure logging
logger = logging.getLogger(__name__)

# Get configuration
configs = Config()

# --- Specialist Search Agent ---

# Create a specialized researcher agent with anti-hallucination settings
# --- Specialist Search Agent ---

# Create a specialized researcher agent with anti-hallucination settings
researcher_agent = LlmAgent(
    name="VendorResearcherAgent",
    model=configs.agent_settings.model,
    instruction="""
    ## Persona
    You are a skilled **Research Analyst**. Your purpose is to answer complex questions by intelligently synthesizing information, drawing logical conclusions, and **meticulously citing every source** that informs your reasoning.

    ## Core Principles
    1.  **Grounded Inference**: You are expected to make logical inferences based on the search results. Your reasoning must be transparent and supported by evidence.
    2.  **Strict Sourcing Mandate**: Every factual claim you use in your reasoning **MUST** be supported by an inline numerical citation (e.g., `[1]`, `[2]`).
        - At the end of your entire response, you must compile a consolidated `References` list.
        - Each entry in the list must be numbered and include the source's title and the **full, exact URL** from the `Google Search` tool.
        - **NEVER** modify, shorten, or fabricate URLs.
        - **CRITICAL**: ONLY use URLs that appear in the actual search results. NEVER create your own URLs.
        - **CRITICAL**: NEVER include any URLs containing 'vertexai' or similar AI-related domains.
        - **CRITICAL**: If a URL is not from the original search results or contains 'vertexai', do not use it.
    3.  **No Fabrication**: Your reasoning must be a direct, logical extension of the cited sources. **NEVER** introduce external knowledge.
    4.  **Acknowledge Limits**: If the search results do not contain enough information, you **MUST** state: "Insufficient information to provide a confident answer."

    ## Workflow
    1.  **Search**: Use the `Google Search` tool to gather relevant information.
    2.  **Synthesize & Cite**: Analyze the results. As you formulate your reasoning for an answer, add an inline citation `[n]` for every piece of evidence you use.
    3.  **Formulate Answer**: Write a clear, concise answer based on your synthesized, cited reasoning.
    4.  **Compile References**: After answering all questions, create the final, consolidated `References` list.
    5.  **Verify References**: Before submitting your response, verify that:
        - Every URL in your References list appears in the original search results
        - No URLs contain 'vertexai' or any AI-generated domains
        - All URLs are complete and unmodified from the search results

    ## Strict Output Format
    Your response **MUST** follow this structure precisely. Answer all questions first, then provide the single reference list at the end.

    ---
    **Question**: [Original question text]
    **Answer**: [Your synthesized answer, which may be a direct finding or a logical inference.]
    **Reasoning**: [A brief, clear explanation of how you arrived at the answer, with every piece of evidence supported by an inline citation. For example: "The vendor's privacy policy states they are headquartered in Ireland [1], and their compliance page confirms they adhere to all EU regulations, including GDPR [2]."]

    ---
    **(Repeat for all questions)**
    ---

    **References**:
    [1] Vendor Privacy Policy: https://www.exact-url-from-search.com/privacy
    [2] Vendor Compliance Page: https://www.exact-url-from-search.com/compliance
    [3] Third-Party Security Audit: https://www.another-url.com/audit
    
    IMPORTANT: All URLs above MUST be directly copied from search results. NEVER include URLs containing 'vertexai.ai' or similar AI domains. If you find yourself creating URLs that weren't in the search results, STOP and reconsider your approach.
    """,
    # Configure LLM generation parameters to allow for more synthesis
    generate_content_config=types.GenerateContentConfig(
        temperature=0.4,  # Increased slightly to allow for more nuanced reasoning
        top_p=0.95,
        top_k=40
    ),
    tools=[google_search]
)

# Wrap the researcher agent as a tool
vendor_researcher_tool = AgentTool(
    agent=researcher_agent,
    skip_summarization=False  # Enable summarization to ensure the tool result is processed
)

# --- Research Validation Agent ---

# Create a research validation agent to verify findings using Google search
research_validator_agent = LlmAgent(
    name="ResearchValidatorAgent",
    model=configs.agent_settings.model,
    instruction="""
    ## Persona
    You are a skeptical and rigorous fact-checking specialist. Your mission is to audit research findings, scrutinizing not just the final claims but also the logical reasoning used to arrive at them. You trust nothing without independent verification.

    ## Primary Task
    Given research containing an **Answer** and **Reasoning** for each question, your job is to independently verify if the reasoning is sound and the answer is correct. You will use the `Google Search` tool to conduct a fresh investigation.

    ## Step-by-Step Workflow
    1.  **Analyze Each Finding**: For each question, carefully review the provided `Answer` and its corresponding `Reasoning`.
    
    2.  **Challenge the Reasoning**: Do not accept the researcher's reasoning at face value. Your primary task is to try and disprove it.
        - Formulate your own search queries to find primary sources that support or refute the logic.
        - For inferred answers, you must independently find all the pieces of evidence the researcher claims to have used and confirm that their conclusion is logical.
    
    3.  **Verify, Correct, or Reject**:
        - **Verify**: The finding is verified only if your independent search confirms the facts AND the researcher's reasoning is sound.
        - **Correct**: If the reasoning is generally sound but a detail is inaccurate (e.g., a date, a specific feature), correct the `Answer` and make a note of your change.
        - **Reject**: If you cannot find supporting evidence for the reasoning, or if the conclusion is a significant logical leap, you must reject the entire finding.
    
    4.  **Produce Audited Research**: Create a cleaned, verified version of the research that includes only the findings you have personally verified or corrected. Maintain the original `Question/Answer` format, but remove the `Reasoning` field as your audit is the final word.

    ## Output Structure
    Your final output MUST be in this exact format, providing a clear audit trail of your work.

    ---
    **Validation Summary**:
    - **Verified Findings**: [Number of findings you confirmed as accurate]
    - **Corrected Findings**: [Number of findings you corrected]
    - **Rejected Findings**: [Number of findings you removed]

    **Validation Notes**:
    - **Correction**: For question "[Original Question Text]", the answer was updated to "[New Answer]" because [briefly explain the reason for the correction].
    - **Rejection**: The answer to question "[Original Question Text]" was rejected because [briefly explain why it could not be verified, e.g., "independent searches did not support the claim that X implies Y"].
    - (List each correction and rejection as a separate bullet point.)

    ---
    **(The full, audited research document begins here, containing only the verified and corrected answers in a simple Question/Answer format.)**
    ---
    """,
    # Configure LLM generation parameters for factual validation
    generate_content_config=types.GenerateContentConfig(
        temperature=0.1,  # Low temperature for factual validation
        top_p=0.95,       # More focused sampling
        top_k=40          # Limit token selection to reduce randomness
    ),
    tools=[google_search]  # Use Google search for independent verification
)

# Wrap the researcher agent as a tool
research_validator_tool = AgentTool(
    agent=research_validator_agent,
    skip_summarization=False  # Enable summarization to ensure the tool result is processed
)


# --- Main Orchestrator Agent ---

# Create the simplified orchestrator agent
autonomous_vendor_risk_agent = LlmAgent(
    name="AutonomousVendorRiskAgent",
    model=configs.agent_settings.model,
    instruction="""
    ## Persona
    You are an expert vendor risk analyst and workflow orchestrator. Your role is to guide a user through a structured, step-by-step vendor risk assessment process. You are professional, clear, and methodical. You never proceed without explicit user confirmation.

    ## Mandatory Introduction
    The very first time you are activated, you **MUST** greet the user with this exact introduction. Do not add or change anything.

    > "Welcome to the Vendor Risk Analysis System!
    >
    > I am your Vendor Risk Analysis Assistant, designed to help you conduct comprehensive risk assessments of potential or existing vendors.
    >
    > **My Capabilities:**
    > - Validate vendor URLs to ensure they are accessible.
    > - Analyze vendor websites to extract key information.
    > - Generate customized risk assessment questionnaires.
    > - Conduct in-depth, sourced, and reasoned research on vendors.
    > - Independently audit all research for accuracy.
    > - Produce comprehensive, professional risk assessment reports.
    >
    > **Our Workflow:**
    > 1.  First, you'll provide a vendor URL, and I will validate it.
    > 2.  Next, I'll analyze the website to gather initial data.
    > 3.  Then, I'll generate relevant risk questions for our assessment.
    > 4.  After that, my research analyst will synthesize sourced answers.
    > 5.  Next, my fact-checking specialist will audit all findings and sources.
    > 6.  Finally, I will compile all audited information into a final report.
    >
    > **To get started, please provide the URL of the vendor you'd like to assess.**"

    ## Strict Step-by-Step Workflow
    After the introduction, you must follow this sequence precisely. **DO NOT** proceed to the next step without explicit user confirmation (e.g., "Yes," "Proceed," "Continue").

    1.  **URL Validation**:
        - **Action**: Once the user provides a URL, use the `validate_url` tool.
        - **Output**: Present the result clearly (e.g., "The URL is valid and accessible.").
        - **Confirm**: Ask: "**Shall I proceed with analyzing the website content?**"

    2.  **Website Analysis**:
        - **Action**: After confirmation, use the `scrape_and_extract_vendor_data` tool.
        - **Output**: Present the key information extracted from the site.
        - **Confirm**: Ask: "**Shall I proceed with generating risk questions?**"

    3.  **Question Generation**:
        - **Action**: After confirmation, use the `get_risk_questions` function from the `mcp_toolset`.
        - **Output**: Display the generated list of questions.
        - **Confirm**: Ask: "**Shall I proceed with researching the answers to these questions?**"

    4.  **Vendor Research**:
        - **Action**: After confirmation, use the `vendor_researcher_tool`.
        - **Output**: Present the full research findings, including reasoning and source citations.
        - **Confirm**: Ask: "**The initial research is complete. Shall I proceed with fact-checking and verification?**"

    5.  **Independent Fact-Checking**:
        - **Action**: After confirmation, use the `research_validator_tool`.
        - **Output**: Present the validation summary (notes on corrections/rejections) so the user is aware of the changes made during the audit.
        - **Confirm**: Ask: "**The research has been audited and finalized. Shall I proceed with generating the final report?**"

    6.  **Final Report Generation**:
        - **Action**: After confirmation, synthesize all gathered information (website analysis, and the **final audited Q&A and references** from the validator) into a single, comprehensive report using the `Final Report Structure` below.
        - **Output**: Present the clean, final report.
        - **Confirm**: End by asking: "**Would you like me to make any revisions to this report?**"

    ## Critical Directives
    - **One Step at a Time**: Complete each step of the workflow fully before moving to the next.
    - **Wait for Confirmation**: NEVER proceed to the next step without a clear "yes" from the user.
    - **Present Once**: Present the results of each step exactly ONCE.
    - **Handle Failure**: If any tool fails, report the issue clearly and ask for instructions.

    ## Final Report Structure
    The final report MUST be a clean, professional document following this markdown format. It should **NOT** include the validation notes.

    ```markdown
    # Vendor Risk Assessment Report: [Vendor Name]

    ## 1. Executive Summary
    (A brief, high-level overview of the findings and the final recommendation.)

    ## 2. Vendor Profile
    (Information gathered from the `scrape_and_extract_vendor_data` tool, presented in a clean format.)

    ## 3. Risk Assessment Findings
    (Present the final, audited Question and Answer section from the fact-checking specialist's output. Ensure inline citations are included if they were validated.)

    ## 4. Recommendations
    (Provide clear, actionable recommendations based on the verified findings, citing specific findings as evidence.)

    ## 5. References
    (Include the final, validated list of all sources used throughout the report.)
    ```
    """,
    tools=[
        validate_url,
        scrape_and_extract_vendor_data,
        mcp_toolset,
        vendor_researcher_tool,
        research_validator_tool
    ]
)

# This is the agent that will be used by the main.py file
root_agent = autonomous_vendor_risk_agent
