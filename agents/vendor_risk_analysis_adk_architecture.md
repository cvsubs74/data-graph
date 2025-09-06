# Vendor Risk Analysis System: ADK Implementation Architecture

## Overview

This document outlines the implementation architecture for a multi-agent vendor risk analysis system using Google's Agent Development Kit (ADK). The system is designed to process multiple vendors in parallel, conduct comprehensive risk assessments, and produce verified, professional reports.

## System Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                                                                                     │
│                        VENDOR RISK ANALYSIS SYSTEM                                  │
│                                                                                     │
├─────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                     │
│  ┌───────────────────────────────────────────────────────────────────────────────┐  │
│  │                          VendorRiskCoordinatorAgent                           │  │
│  │                           (Custom Agent extends BaseAgent)                    │  │
│  └───────────────────────────────────────────────────────────────────────────────┘  │
│                                         │                                            │
│                                         ▼                                            │
│  ┌───────────────────────────────────────────────────────────────────────────────┐  │
│  │                             ParallelAgent                                     │  │
│  │                                                                               │  │
│  │    ┌─────────────────┐      ┌─────────────────┐      ┌─────────────────┐     │  │
│  │    │ Vendor Pipeline │      │ Vendor Pipeline │      │ Vendor Pipeline │     │  │
│  │    │    (Vendor 1)   │      │    (Vendor 2)   │      │    (Vendor N)   │     │  │
│  │    └─────────────────┘      └─────────────────┘      └─────────────────┘     │  │
│  └───────────────────────────────────────────────────────────────────────────────┘  │
│                                                                                     │
├─────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                     │
│                           VENDOR PIPELINE (PER VENDOR)                              │
│                                                                                     │
├─────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                     │
│  ┌───────────────────────────────────────────────────────────────────────────────┐  │
│  │                             SequentialAgent                                   │  │
│  │                                                                               │  │
│  │    ┌─────────────┐     ┌─────────────┐     ┌─────────────┐     ┌─────────────┐  │
│  │    │             │     │             │     │             │     │             │  │
│  │    │ Initializer │────▶│ Researcher  │────▶│  Analyst    │────▶│ Verifier &  │  │
│  │    │   Agent     │     │   Agent     │     │   Agent     │     │  Reporter   │  │
│  │    │  (LlmAgent) │     │  (LlmAgent) │     │  (LlmAgent) │     │  (LlmAgent) │  │
│  │    │             │     │             │     │             │     │             │  │
│  │    └─────────────┘     └─────────────┘     └─────────────┘     └─────────────┘  │
│  │          │                   │                   │                   │           │
│  │          ▼                   ▼                   ▼                   ▼           │
│  │    ┌─────────────┐     ┌─────────────┐     ┌─────────────┐     ┌─────────────┐  │
│  │    │ initial_data│     │research_data│     │answered_data│     │   Final     │  │
│  │    │  - URL      │     │  - URL      │     │  - URL      │     │   Report    │  │
│  │    │  - Summary  │     │  - Research │     │  - Research │     │ (Markdown)  │  │
│  │    └─────────────┘     └─────────────┘     │  - Q&A      │     └─────────────┘  │
│  │                                            └─────────────┘                       │
│  └───────────────────────────────────────────────────────────────────────────────┘  │
│                                                                                     │
├─────────────────────────────────────────────────────────────────────────────────────┤
│                                 BACKEND SERVICES                                     │
├─────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                     │
│  ┌─────────────────┐     ┌─────────────────┐     ┌─────────────────────────────┐   │
│  │                 │     │                 │     │                             │   │
│  │  Web Scraper    │     │  Search Engine  │     │     Risk Questions MCP      │   │
│  │     Tool        │     │      Tool       │     │          Service            │   │
│  │                 │     │                 │     │                             │   │
│  └─────────────────┘     └─────────────────┘     └─────────────────────────────┘   │
│                                                                                     │
└─────────────────────────────────────────────────────────────────────────────────────┘
```

## ADK Component Implementation

### 1. Core Components

#### VendorRiskCoordinatorAgent (Custom Agent)

This is the top-level agent that coordinates the entire vendor risk analysis process. It's implemented as a custom agent by extending `BaseAgent`.

```python
from google.adk.agents import BaseAgent, ParallelAgent, SequentialAgent, LlmAgent
from google.adk.agents.invocation_context import InvocationContext
from typing import AsyncGenerator, List

class VendorRiskCoordinatorAgent(BaseAgent):
    """
    Top-level coordinator agent that processes multiple vendor requests in parallel.
    """
    parallel_agent: ParallelAgent
    
    def __init__(self, name: str, vendor_names: List[str]):
        """
        Initialize the coordinator with a list of vendor names to analyze.
        """
        # Create vendor pipelines for each vendor
        vendor_pipelines = []
        for vendor_name in vendor_names:
            vendor_pipeline = self._create_vendor_pipeline(vendor_name)
            vendor_pipelines.append(vendor_pipeline)
        
        # Create a parallel agent to process all vendors concurrently
        self.parallel_agent = ParallelAgent(
            name="VendorParallelProcessor",
            sub_agents=vendor_pipelines
        )
        
        super().__init__(name=name)
    
    def _create_vendor_pipeline(self, vendor_name: str) -> SequentialAgent:
        """
        Create a sequential pipeline for processing a single vendor.
        """
        # Create the four specialized agents for this vendor
        initializer = self._create_initializer_agent(vendor_name)
        researcher = self._create_researcher_agent()
        analyst = self._create_analyst_agent()
        verifier = self._create_verifier_agent()
        
        # Create a sequential pipeline to process this vendor
        return SequentialAgent(
            name=f"VendorPipeline_{vendor_name}",
            sub_agents=[initializer, researcher, analyst, verifier]
        )
    
    async def _run_async_impl(self, ctx: InvocationContext) -> AsyncGenerator:
        """
        Execute the vendor risk analysis workflow.
        """
        # Run all vendor pipelines in parallel
        async for event in self.parallel_agent.run_async(ctx):
            yield event
        
        # After all vendors are processed, generate a summary
        yield self._generate_summary(ctx)
```

### 2. Specialized Agent Implementation

#### Pydantic Schemas for Data Exchange

```python
from pydantic import BaseModel, Field
from typing import Optional, List, Dict

# Schemas for Initializer Agent
class VendorInput(BaseModel):
    vendor_name: str = Field(description="The name of the vendor to analyze")
    vendor_url: Optional[str] = Field(None, description="The URL of the vendor's website")

class InitialData(BaseModel):
    vendor_name: str = Field(description="The name of the vendor")
    vendor_url: str = Field(description="The URL of the vendor's website")
    vendor_summary: str = Field(description="A concise 2-3 sentence summary of the vendor's business")

# Schemas for Researcher Agent
class ResearchData(BaseModel):
    vendor_name: str = Field(description="The name of the vendor")
    vendor_url: str = Field(description="The URL of the vendor's website")
    research_output: str = Field(description="Comprehensive research findings on the vendor")

# Schemas for Analyst Agent
class RiskQuestion(BaseModel):
    question_id: str = Field(description="Unique identifier for the question")
    question_text: str = Field(description="The text of the question")
    question_type: str = Field(description="Type of question (yes/no, free_text, single_select)")
    category: str = Field(description="Risk category the question belongs to")
    options: Optional[List[Dict[str, str]]] = Field(None, description="Options for single_select questions")

class AnsweredQuestion(BaseModel):
    question_id: str = Field(description="Unique identifier for the question")
    question_text: str = Field(description="The text of the question")
    answer: str = Field(description="The answer to the question")
    source: Optional[str] = Field(None, description="Source of the answer")

class AnsweredData(BaseModel):
    vendor_name: str = Field(description="The name of the vendor")
    vendor_url: str = Field(description="The URL of the vendor's website")
    research_summary: str = Field(description="Summary of the research findings")
    answered_questions: List[AnsweredQuestion] = Field(description="List of questions with answers")

# Schema for Verifier & Reporter Agent
class FinalReport(BaseModel):
    vendor_name: str = Field(description="The name of the vendor")
    vendor_url: str = Field(description="The URL of the vendor's website")
    executive_summary: str = Field(description="Executive summary of the risk analysis")
    risk_assessment: str = Field(description="Overall risk assessment")
    detailed_findings: str = Field(description="Detailed findings by category")
    verification_sources: List[str] = Field(description="Sources used to verify information")
    recommendations: str = Field(description="Recommendations based on the risk analysis")
    markdown_report: str = Field(description="Complete formatted markdown report")
```

#### Initializer Agent (LlmAgent)

```python
def _create_initializer_agent(self, vendor_name: str) -> LlmAgent:
    """
    Create an LlmAgent that initializes the vendor analysis process.
    """
    return LlmAgent(
        name=f"Initializer_{vendor_name}",
        model="gemini-2.0-pro",
        instruction=f"""
        You are the Initializer Agent for vendor risk analysis.
        
        Your task is to gather and confirm basic information about {vendor_name}.
        
        1. If the vendor URL is not provided, ask the user for it.
        2. Use the web_scraper tool to extract content from the vendor's website.
        3. Generate a concise 2-3 sentence summary of the vendor's business.
        4. Present the summary to the user and explicitly ask for confirmation to proceed.
        5. Wait for explicit user confirmation before proceeding.
        
        IMPORTANT: You must ALWAYS ask for explicit user confirmation before proceeding.
        Use standardized confirmation phrases like "Would you like me to proceed with..."
        
        Your output should be structured according to the InitialData schema.
        """,
        tools=[web_scraper_tool],
        input_schema=VendorInput,
        output_key="initial_data"
    )
```

#### Researcher Agent (LlmAgent)

```python
def _create_researcher_agent(self) -> LlmAgent:
    """
    Create an LlmAgent that conducts comprehensive research on the vendor.
    """
    return LlmAgent(
        name="Researcher",
        model="gemini-2.0-pro",
        instruction="""
        You are the Researcher Agent for vendor risk analysis.
        
        Your task is to conduct comprehensive research on the vendor using the information provided.
        
        1. Use the search_engine tool to gather detailed information about the vendor.
        2. Focus on risk-relevant information:
           - Company history and background
           - Financial stability and performance
           - Security incidents and breaches
           - Regulatory compliance history
           - Customer reviews and satisfaction
           - Legal disputes and litigation
           - Market reputation and industry standing
        3. Synthesize your findings into a structured research document.
        4. Present your research to the user and explicitly ask for confirmation to proceed.
        5. Wait for explicit user confirmation before proceeding.
        
        IMPORTANT: You must ALWAYS ask for explicit user confirmation before proceeding.
        Use standardized confirmation phrases like "Would you like me to proceed with..."
        
        Your output should be structured according to the ResearchData schema.
        """,
        tools=[search_engine_tool],
        input_schema=InitialData,
        output_key="research_data"
    )
```

#### Analyst Agent (LlmAgent)

```python
def _create_analyst_agent(self) -> LlmAgent:
    """
    Create an LlmAgent that applies the standardized risk framework.
    """
    return LlmAgent(
        name="Analyst",
        model="gemini-2.0-pro",
        instruction="""
        You are the Analyst Agent for vendor risk analysis.
        
        Your task is to apply a standardized risk assessment framework to the research findings.
        
        1. Use the get_risk_questions tool to fetch the standardized list of questions.
        2. For each question, find the answer within the research data.
        3. For any questions that cannot be answered from the existing research, use the search_engine tool to find specific answers.
        4. Compile a complete list of questions and their corresponding answers.
        5. Present your analysis to the user and explicitly ask for confirmation to proceed.
        6. Wait for explicit user confirmation before proceeding.
        
        IMPORTANT: 
        - You must ALWAYS ask for explicit user confirmation before proceeding.
        - Use standardized confirmation phrases like "Would you like me to proceed with..."
        - Present information in a business-friendly format without technical details.
        - Do not show similarity scores or technical metrics to users.
        
        Your output should be structured according to the AnsweredData schema.
        """,
        tools=[get_risk_questions_tool, search_engine_tool],
        input_schema=ResearchData,
        output_key="answered_data"
    )
```

#### Verifier & Reporter Agent (LlmAgent)

```python
def _create_verifier_agent(self) -> LlmAgent:
    """
    Create an LlmAgent that verifies findings and generates the final report.
    """
    return LlmAgent(
        name="Verifier",
        model="gemini-2.0-pro",
        instruction="""
        You are the Verifier & Reporter Agent for vendor risk analysis.
        
        Your task is to ensure the accuracy of the analysis and generate a professional final report.
        
        1. Review the key claims, facts, and answers in the research document.
        2. Use the search_engine tool to find corroborating sources for key points.
        3. Correct any discrepancies found during verification.
        4. Format the entire verified analysis into a clean, well-structured Markdown file.
        5. The report should include clear headings for each section:
           - Executive Summary
           - Vendor Overview
           - Risk Assessment Results
           - Detailed Findings (by category)
           - Verification Sources
           - Recommendations
        6. Present the final report to the user.
        
        IMPORTANT:
        - Present information in a business-friendly format without technical details.
        - Do not show similarity scores or technical metrics to users.
        
        Your output should be structured according to the FinalReport schema.
        """,
        tools=[search_engine_tool],
        input_schema=AnsweredData,
        output_key="final_report"
    )
```

### 3. Tool Definitions

```python
from google.adk.tools import Tool, ToolSpec

# Web Scraper Tool
web_scraper_tool = Tool(
    name="web_scraper",
    description="Extracts content from a vendor's website",
    spec=ToolSpec(
        parameters={
            "url": {
                "type": "string",
                "description": "The URL of the vendor's website"
            }
        },
        returns={
            "content": {
                "type": "string",
                "description": "The extracted content from the website"
            }
        }
    ),
    function=web_scraper_function
)

# Search Engine Tool
search_engine_tool = Tool(
    name="search_engine",
    description="Performs web searches for vendor information",
    spec=ToolSpec(
        parameters={
            "query": {
                "type": "string",
                "description": "The search query"
            }
        },
        returns={
            "results": {
                "type": "array",
                "description": "The search results"
            }
        }
    ),
    function=search_engine_function
)

# Risk Questions Tool
get_risk_questions_tool = Tool(
    name="get_risk_questions",
    description="Retrieves standardized risk assessment questions",
    spec=ToolSpec(
        parameters={
            "category": {
                "type": "string",
                "description": "Optional category filter",
                "required": False
            }
        },
        returns={
            "questions": {
                "type": "array",
                "description": "List of risk assessment questions"
            }
        }
    ),
    function=get_risk_questions_function
)
```

## State Management

The system uses ADK's session state with Pydantic models to pass structured data between agents in the pipeline:

```python
# Example of state flow through the pipeline using Pydantic models

# Initializer Agent sets initial data using the InitialData schema
# This happens automatically because of output_key="initial_data"
initial_data = InitialData(
    vendor_name="Example Vendor",
    vendor_url="https://example.com",
    vendor_summary="Example Vendor is a cloud storage provider specializing in healthcare information systems."
)
ctx.session.state["initial_data"] = initial_data

# Researcher Agent reads initial data and sets research data
# The input_schema=InitialData parameter ensures the agent receives properly structured data
# The output is automatically stored in state with output_key="research_data"
research_data = ResearchData(
    vendor_name=initial_data.vendor_name,
    vendor_url=initial_data.vendor_url,
    research_output="# Research findings on Example Vendor\n\n## Company Background\nExample Vendor was founded in 2015...\n\n## Security History\nThe company has maintained SOC 2 compliance..."
)
ctx.session.state["research_data"] = research_data

# Analyst Agent reads research data and sets answered data
# The input_schema=ResearchData parameter ensures the agent receives properly structured data
# The output is automatically stored in state with output_key="answered_data"
answered_questions = [
    AnsweredQuestion(
        question_id="q1",
        question_text="Does the vendor have SOC 2 certification?",
        answer="Yes, Example Vendor has maintained SOC 2 compliance since 2018.",
        source="Company website security page"
    ),
    AnsweredQuestion(
        question_id="q2",
        question_text="Has the vendor experienced any data breaches in the last 5 years?",
        answer="No reported breaches were found in public records or the vendor's disclosure statements.",
        source="Security breach database search"
    )
]
answered_data = AnsweredData(
    vendor_name=research_data.vendor_name,
    vendor_url=research_data.vendor_url,
    research_summary="Example Vendor demonstrates strong security practices with SOC 2 compliance...",
    answered_questions=answered_questions
)
ctx.session.state["answered_data"] = answered_data

# Verifier Agent reads answered data and sets final report
# The input_schema=AnsweredData parameter ensures the agent receives properly structured data
# The output is automatically stored in state with output_key="final_report"
final_report = FinalReport(
    vendor_name=answered_data.vendor_name,
    vendor_url=answered_data.vendor_url,
    executive_summary="Example Vendor presents a low risk profile based on our analysis...",
    risk_assessment="LOW RISK: The vendor demonstrates strong security practices...",
    detailed_findings="## Security Posture\nThe vendor maintains SOC 2 compliance...",
    verification_sources=["SOC 2 certification database", "Security breach database"],
    recommendations="Based on our analysis, we recommend proceeding with this vendor...",
    markdown_report="# Vendor Risk Analysis Report for Example Vendor\n\n## Executive Summary\n..."
)
ctx.session.state["final_report"] = final_report
```

### Benefits of Using Pydantic Schemas with ADK

1. **Type Safety**: The `input_schema` parameter ensures that agents receive properly structured data, preventing runtime errors.

2. **Validation**: Pydantic automatically validates data against the schema, ensuring all required fields are present and have the correct types.

3. **Documentation**: The schemas serve as self-documenting code, making it clear what data each agent expects and produces.

4. **IDE Support**: Developers get autocomplete and type hints when working with the schema objects.

5. **Consistent Data Flow**: The schemas enforce a consistent data structure throughout the agent pipeline.

## User Interaction and Confirmation

The system implements explicit user confirmation at key points in the workflow:

1. Each agent includes instructions to explicitly ask for user confirmation
2. Agents use standardized confirmation phrases like "Would you like me to proceed with..."
3. Agents wait for explicit user response before proceeding
4. If the user provides feedback or requests changes, agents make those changes before proceeding

## Implementation Considerations

### 1. Error Handling

```python
# Example error handling in the coordinator agent
async def _run_async_impl(self, ctx: InvocationContext) -> AsyncGenerator:
    try:
        async for event in self.parallel_agent.run_async(ctx):
            yield event
    except Exception as e:
        # Log the error
        logging.error(f"Error in vendor risk analysis: {e}")
        # Provide user-friendly error message
        yield f"An error occurred during the vendor risk analysis: {e}. Please try again."
```

### 2. Callbacks for Monitoring

```python
from google.adk.callbacks import Callback, CallbackContext

class VendorRiskAnalysisCallback(Callback):
    """Callback for monitoring the vendor risk analysis process."""
    
    def on_agent_start(self, ctx: CallbackContext) -> None:
        """Called when an agent starts execution."""
        agent_name = ctx.agent.name
        logging.info(f"Starting agent: {agent_name}")
    
    def on_agent_end(self, ctx: CallbackContext) -> None:
        """Called when an agent completes execution."""
        agent_name = ctx.agent.name
        logging.info(f"Completed agent: {agent_name}")
    
    def on_tool_call(self, ctx: CallbackContext) -> None:
        """Called when a tool is invoked."""
        tool_name = ctx.tool_call.name
        logging.info(f"Tool called: {tool_name}")
```

### 3. MCP Integration

The system integrates with the Model Context Protocol (MCP) for standardized communication with backend services:

```python
from google.adk.mcp import McpClient

# Initialize MCP client
mcp_client = McpClient(server_url="https://mcp-server.example.com")

# Example function for the get_risk_questions tool
async def get_risk_questions_function(category=None):
    """Retrieve risk assessment questions from the MCP server."""
    # Build the request
    request = {
        "operation": "get_risk_questions"
    }
    if category:
        request["category"] = category
    
    # Send the request to the MCP server
    response = await mcp_client.execute(request)
    
    # Return the questions
    return response["questions"]
```

## Deployment and Execution

To deploy and run the vendor risk analysis system with Pydantic schemas:

```python
from google.adk.runtime import Runtime
from google.adk.sessions import InMemorySessionService
from google.adk.runners import Runner
from pydantic import BaseModel, Field
from typing import List, Optional, Dict

# Import all the Pydantic schemas defined earlier
# VendorInput, InitialData, ResearchData, etc.

# Create the coordinator agent
coordinator = VendorRiskCoordinatorAgent(
    name="VendorRiskCoordinator",
    vendor_names=["Vendor1", "Vendor2", "Vendor3"]
)

# Register the callback
callback = VendorRiskAnalysisCallback()

# Create the session service and runner
session_service = InMemorySessionService()
runner = Runner(
    session_service=session_service,
    callbacks=[callback]
)

# Run the coordinator agent
async def main():
    # Create a new session
    session = await session_service.create_session()
    
    # Initialize the session with vendor input data
    vendor_inputs = [
        VendorInput(vendor_name="Vendor1", vendor_url="https://vendor1.com"),
        VendorInput(vendor_name="Vendor2", vendor_url="https://vendor2.com"),
        VendorInput(vendor_name="Vendor3", vendor_url="https://vendor3.com")
    ]
    session.state["vendor_inputs"] = vendor_inputs
    
    # Run the coordinator agent
    result = await runner.run_agent(coordinator, session=session)
    
    # Process the final reports
    final_reports = []
    for vendor_name in ["Vendor1", "Vendor2", "Vendor3"]:
        report_key = f"final_report_{vendor_name}"
        if report_key in session.state:
            final_report = session.state[report_key]
            if isinstance(final_report, FinalReport):
                final_reports.append(final_report)
    
    # Print summary of results
    print(f"Analysis complete for {len(final_reports)} vendors")
    for report in final_reports:
        print(f"- {report.vendor_name}: {report.risk_assessment}")

# Execute the main function
if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
```

## Conclusion

This ADK implementation architecture provides a robust, scalable solution for vendor risk analysis. By leveraging ADK's agent types (LlmAgent, SequentialAgent, ParallelAgent, and custom BaseAgent), the system can process multiple vendors in parallel while maintaining a structured, deterministic workflow for each vendor.

The architecture ensures:

1. **Explicit User Confirmation** at every stage of the process
2. **Business-Friendly Presentation** without technical details
3. **Parallel Processing** of multiple vendors
4. **Standardized Assessment** using backend risk question services
5. **Professional Reporting** with verified information

This implementation follows ADK best practices for state management, error handling, and agent composition, resulting in a reliable and maintainable system.
