# Vendor Risk Analysis System Architecture

## Introduction

This document provides a comprehensive overview of the vendor risk analysis system architecture. The system is designed to perform thorough assessments of potential vendors by analyzing their websites, researching their security practices, compliance status, and business operations, and generating detailed reports with properly cited sources.

## Architecture Overview

The vendor risk analysis system employs a multi-agent architecture with specialized components working together to deliver a comprehensive vendor assessment. The architecture consists of:

1. **Orchestrator Agent**: A central agent that coordinates the entire workflow and interacts with the user
2. **Specialized Research Agent**: A dedicated agent optimized for in-depth research with advanced reasoning capabilities
3. **Tool Suite**: A collection of specialized tools for web scraping, question generation, and PDF report creation
4. **Backend Services**: Supporting services including MCP server, Google Search API, and Google Cloud Storage
5. **Model Specialization**: Different LLM models optimized for specific tasks (reasoning vs. interaction)

This architecture enables a structured, step-by-step assessment process with explicit user confirmation at each stage, ensuring thorough analysis while maintaining user control throughout the workflow.

## System Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────────┐
│                                                                         │
│                        VENDOR RISK ANALYSIS SYSTEM                      │
│                                                                         │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  ┌───────────────────────────────────────────────────────────────────┐  │
│  │                                                                   │  │
│  │                   Autonomous Vendor Risk Agent                    │  │
│  │                   (Main Orchestrator Agent)                       │  │
│  │                                                                   │  │
│  └───────────────────────────────────────────────────────────────────┘  │
│                    │                  │                 │               │
│                    ▼                  ▼                 ▼               │
│  ┌─────────────────────┐  ┌─────────────────┐  ┌───────────────────┐   │
│  │                     │  │                 │  │                   │   │
│  │ Web Scraper Tool    │  │ MCP Toolset     │  │ Vendor Research  │   │
│  │ (URL Validation)    │  │ (Questions)     │  │ Agent (As Tool)  │   │
│  │                     │  │                 │  │                   │   │
│  └─────────────────────┘  └─────────────────┘  └───────────────────┘   │
│                                                        │               │
│                                                        ▼               │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │                                                                 │   │
│  │                     PDF Report Generator                        │   │
│  │                     (Google Cloud Storage)                      │   │
│  │                                                                 │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                                                         │
├─────────────────────────────────────────────────────────────────────────┤
│                           BACKEND SERVICES                              │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  ┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐   │
│  │                 │     │                 │     │                 │   │
│  │  Web Scraper    │     │  Google Search  │     │ MCP Question    │   │
│  │     Tool        │     │      Tool       │     │     Service     │   │
│  │                 │     │                 │     │                 │   │
│  └─────────────────┘     └─────────────────┘     └─────────────────┘   │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

## Agent Architecture

The vendor risk analysis system employs a sophisticated multi-agent architecture where each agent is specialized for specific tasks in the assessment workflow. This specialization ensures high-quality results while maintaining a seamless user experience.

### 1. Autonomous Vendor Risk Agent (Main Orchestrator)

**Purpose**: Serves as the central coordinator for the entire vendor assessment process, managing user interactions and workflow progression.

**Technical Implementation**:
- **Model**: Gemini-2.5-Flash (optimized for responsive user interaction)
- **Agent Type**: LlmAgent with specialized instruction set
- **Configuration**: Configured via the `agent_settings` in config.py

**Core Responsibilities**:
- Manages the complete assessment workflow from start to finish
- Provides clear explanations of capabilities and process to users
- Enforces explicit user confirmation at each critical decision point
- Coordinates all specialized tools and sub-agents
- Synthesizes information from multiple sources into coherent reports
- Ensures proper source validation and citation throughout the process
- Manages error handling and recovery across the entire workflow

**Key Features**:
- Structured, step-by-step workflow with clear progression
- Explicit user confirmation required at each stage
- Comprehensive instruction set with detailed guidance for each step
- Standardized confirmation phrases for consistency
- Detailed error handling and recovery procedures

**Interaction Pattern**:
- Introduces capabilities and explains the assessment process
- Guides users through each step with clear instructions
- Presents results in a business-friendly format
- Requests explicit confirmation before proceeding to next steps
- Implements user feedback and requested changes before proceeding

### 2. Vendor Research Agent (Specialist Sub-Agent)

**Purpose**: Conducts in-depth, evidence-based research on vendors using advanced reasoning capabilities to answer specific questions with properly cited sources.

**Technical Implementation**:
- **Model**: Gemini-2.5-Pro (optimized for complex reasoning and research tasks)
- **Agent Type**: LlmAgent wrapped as AgentTool for the main orchestrator
- **Configuration**: Uses specialized reasoning_model from config.py

**Core Responsibilities**:
- Performs targeted web searches based on vendor information and specific questions
- Analyzes search results to extract relevant information
- Synthesizes information from multiple sources into coherent answers
- Provides detailed evidence for each answer with proper citations
- Ensures all sources are properly formatted as clickable links
- Verifies source validity and avoids fabricated information

**Key Features**:
- Advanced reasoning capabilities for complex research tasks
- Strict adherence to provided questions without creating new criteria
- Comprehensive source citation with clickable links
- Structured output format organized by question categories
- Clear indication when information is insufficient

**Research Methodology**:
1. Begins with vendor name and URL as primary context
2. Formulates targeted search queries for each specific question
3. Collects evidence from vendor websites and third-party sources
4. Synthesizes findings with inline citations for every factual claim
5. Compiles a consolidated reference list with properly formatted links
6. Provides a summary of key findings across all questions

## Tool Architecture

The vendor risk analysis system employs a comprehensive suite of specialized tools that work together to enable the complete assessment workflow. Each tool is designed for a specific function in the process.

### 1. Web Scraper Tool

**Purpose**: Extracts and analyzes content from vendor websites to gather initial information and validate URLs.

**Technical Implementation**:
- **Function**: `scrape_and_extract_vendor_data` and `validate_url`
- **Dependencies**: BeautifulSoup, Requests, Validators
- **Location**: Implemented in tools.py

**Core Functionalities**:
- Validates URL format and accessibility
- Scrapes complete website content from provided URLs
- Extracts key vendor information including:
  - Company name and description
  - Contact information
  - Product/service offerings
  - Security and compliance information
  - Privacy policy details
- Performs initial content analysis for assessment relevance
- Handles various error conditions (invalid URLs, access issues, etc.)

**Key Features**:
- Robust error handling for various URL formats
- Intelligent extraction of structured data from unstructured HTML
- Proper handling of redirects and security certificates
- Comprehensive validation reporting

### 2. MCP Toolset

**Purpose**: Provides access to standardized assessment questions and other MCP services.

**Technical Implementation**:
- **Class**: MCPToolset with StreamableHTTPConnectionParams
- **Integration**: Connects to vendor_risk_mcp_server
- **Configuration**: Uses MCP_SERVER_URL from config.py

**Core Functionalities**:
- Retrieves standardized question sets based on vendor type
- Organizes questions by category (security, compliance, data privacy, etc.)
- Provides question metadata (type, importance, required status)
- Enables dynamic question generation based on vendor profile

**Key Features**:
- Standardized question format for consistent assessments
- Category-based organization for structured analysis
- Customizable question sets based on vendor characteristics
- Seamless integration with MCP server infrastructure

### 3. PDF Report Generator

**Purpose**: Creates professional, beautifully formatted PDF reports with proper styling and clickable references.

**Technical Implementation**:
- **Function**: `generate_pdf_report`
- **Dependencies**: WeasyPrint, Jinja2, BeautifulSoup, Google Cloud Storage
- **Location**: Implemented in tools.py

**Core Functionalities**:
- Converts markdown content to properly formatted HTML
- Processes and enhances reference links to ensure they're clickable
- Applies professional styling through CSS templates
- Generates high-quality PDF documents
- Uploads PDFs to Google Cloud Storage
- Creates public download URLs for easy access
- Implements fallback to local storage if cloud upload fails

**Key Features**:
- Advanced HTML post-processing for enhanced link functionality
- Beautiful, consistent formatting with professional styling
- Proper handling of long URLs and text wrapping
- Cloud storage integration with configurable bucket settings
- Unique filename generation with vendor name and report ID
- Comprehensive error handling and fallback mechanisms

**Technical Components**:
- HTML template system with Jinja2
- CSS styling framework for professional appearance
- BeautifulSoup for advanced HTML manipulation
- WeasyPrint for high-quality PDF rendering
- Google Cloud Storage integration for file hosting

## Backend Services

The vendor risk analysis system is supported by a robust set of backend services that provide essential functionality for the assessment process. These services are designed to be modular, scalable, and highly reliable.

### 1. Vendor Risk MCP Server

**Purpose**: Provides centralized management of vendor risk assessment questions and categories.

**Technical Implementation**:
- **Server Type**: FastAPI-based microservice
- **Location**: `/backend/vendor_risk_mcp_server/`
- **Configuration**: Configured via environment variables

**Core Functionalities**:
- Manages a comprehensive database of assessment questions
- Organizes questions by category, importance, and type
- Provides RESTful API endpoints for question retrieval
- Enables dynamic question generation based on vendor characteristics
- Supports question customization and extension

**Key Features**:
- High-performance question retrieval with caching
- Standardized question format for consistent assessments
- Flexible question filtering and sorting capabilities
- Secure API access with proper authentication

### 2. Google Search Integration

**Purpose**: Enables comprehensive research capabilities for the vendor research agent.

**Technical Implementation**:
- **Integration**: Google ADK tools google_search
- **Configuration**: Configured via API keys and environment variables

**Core Functionalities**:
- Performs targeted web searches based on vendor information
- Returns comprehensive search results with complete URLs
- Supports advanced query formatting for precise searches
- Enables filtering and sorting of search results

**Key Features**:
- High-quality search results from authoritative sources
- Complete URL information for proper citation
- Support for complex query structures
- Rate limiting and quota management

### 3. Google Cloud Storage

**Purpose**: Provides secure, scalable storage for generated PDF reports with public access capabilities.

**Technical Implementation**:
- **Integration**: Google Cloud Storage client library
- **Configuration**: Configured via GCS_* settings in config.py

**Core Functionalities**:
- Creates and manages storage buckets for report storage
- Handles secure file uploads with proper metadata
- Manages public access permissions for reports
- Generates public download URLs for easy sharing
- Implements proper error handling and retry logic

**Key Features**:
- Configurable bucket names and folder structures
- Automatic creation of buckets if they don't exist
- Public URL generation with configurable formats
- Comprehensive error handling with fallback mechanisms

## Complete Workflow Process

The vendor risk analysis system follows a structured, step-by-step workflow with explicit user confirmation at each stage. This ensures thorough assessment while maintaining user control throughout the process.

### 1. Initialization and Introduction

**Process**:
- System initializes the main orchestrator agent
- Agent introduces itself and explains its capabilities
- Agent outlines the complete assessment workflow
- User is prompted to provide a vendor URL to begin

**Technical Implementation**:
- Orchestrator agent is initialized with the main instruction set
- Introduction text is standardized in the agent's instructions
- User input is captured for the next step

### 2. URL Validation and Initial Analysis

**Process**:
- Agent validates the provided URL for format and accessibility
- Web scraper tool extracts key information from the vendor website
- Initial vendor profile is created based on extracted data
- User is presented with the initial findings
- **Explicit user confirmation** is required before proceeding

**Technical Implementation**:
- `validate_url` function checks URL validity
- `scrape_and_extract_vendor_data` function performs website analysis
- Structured data is extracted from unstructured HTML
- Results are formatted for user presentation

### 3. Question Generation and Customization

**Process**:
- Agent retrieves standardized assessment questions from MCP server
- Questions are organized by category (security, compliance, etc.)
- User is presented with the question set
- User can review, add, remove, or modify questions
- **Explicit user confirmation** is required before proceeding

**Technical Implementation**:
- MCP toolset connects to vendor_risk_mcp_server
- `get_risk_questions` function retrieves appropriate questions
- Questions are formatted for user presentation
- User input is captured for customization

### 4. In-Depth Research and Analysis

**Process**:
- Vendor Research Agent is activated with the question set
- Agent performs targeted searches for each question
- Evidence is collected from vendor websites and third-party sources
- Answers are formulated with proper source citations
- Research findings are presented to the user
- **Explicit user confirmation** is required before proceeding

**Technical Implementation**:
- Vendor Researcher Agent is invoked as a tool
- Google Search tool is used for information gathering
- Advanced reasoning model processes search results
- Structured output is generated with inline citations

### 5. Report Generation and Validation

**Process**:
- Agent compiles all findings into a comprehensive report
- All reference URLs are validated for accessibility
- Report is formatted with proper sections and citations
- User is presented with the complete report
- **Explicit user confirmation** is required before proceeding

**Technical Implementation**:
- Report is generated in markdown format
- `validate_url` function checks all reference URLs
- Report structure follows standardized template
- User input is captured for feedback

### 6. PDF Generation and Delivery

**Process**:
- User requests PDF version of the report
- Markdown report is converted to beautifully formatted PDF
- PDF is uploaded to Google Cloud Storage
- Public download URL is generated and provided to user
- User receives the final report with download link

**Technical Implementation**:
- `generate_pdf_report` function handles PDF creation
- Markdown is converted to HTML with Jinja2 templates
- HTML is processed to ensure clickable links
- WeasyPrint generates the final PDF
- Google Cloud Storage client handles file upload
- Public URL is generated for easy access

## Technical Implementation Details

### Configuration Management

The vendor risk analysis system uses a centralized configuration system to manage all settings and parameters:

**Implementation**:
- **Class**: `Config` class in `config.py`
- **Framework**: Pydantic BaseSettings for robust configuration management
- **Environment Variables**: Support for .env files and system environment variables

**Key Configuration Areas**:
- **Agent Models**: Configuration for different LLM models (flash vs. reasoning)
- **MCP Server**: Connection settings for the vendor risk MCP server
- **Google Cloud**: Project ID, location, and authentication settings
- **Storage**: Bucket names, folder structures, and URL formats for PDF storage

**Features**:
- Type validation for all configuration parameters
- Default values for quick deployment
- Environment variable overrides for flexible deployment
- Nested configuration objects for organized settings

### Agent Implementation

The system uses Google's Agent Development Kit (ADK) for agent implementation:

**Implementation**:
- **Framework**: Google ADK for agent development
- **Agent Types**: LlmAgent for both orchestrator and researcher
- **Tool Integration**: AgentTool wrapper for sub-agent integration

**Key Components**:
- **Instruction Sets**: Detailed instructions for each agent role
- **Tool Registration**: Tools registered with agents for function calling
- **Model Configuration**: Specialized settings for different reasoning tasks

**Advanced Features**:
- Agent-as-tool pattern for hierarchical agent structures
- Specialized model selection based on task complexity
- Comprehensive instruction sets with detailed guidance

### PDF Generation Pipeline

The PDF generation system uses a sophisticated pipeline for high-quality reports:

**Implementation**:
- **Conversion**: Markdown → HTML → PDF pipeline
- **Templating**: Jinja2 for HTML template rendering
- **Styling**: Custom CSS for professional appearance
- **Processing**: BeautifulSoup for HTML enhancement
- **Rendering**: WeasyPrint for PDF generation
- **Storage**: Google Cloud Storage for file hosting

**Pipeline Stages**:
1. **Markdown Processing**: Enhanced markdown with proper link formatting
2. **HTML Generation**: Template-based HTML with dynamic content
3. **Post-Processing**: BeautifulSoup for link enhancement and structure improvements
4. **PDF Rendering**: High-quality PDF generation with proper styling
5. **Cloud Upload**: Secure upload to Google Cloud Storage
6. **URL Generation**: Public URL creation for easy access

**Error Handling**:
- Comprehensive try/except blocks at each stage
- Fallback mechanisms for cloud storage failures
- Detailed logging for troubleshooting
- Graceful degradation when services are unavailable

### Security Considerations

The system implements several security measures to protect data and ensure proper operation:

**URL Validation**:
- Format checking for malicious URLs
- Accessibility verification before processing
- Proper error handling for invalid URLs

**Cloud Storage**:
- Secure authentication for Google Cloud services
- Proper bucket permissions for file access
- Sanitized filenames to prevent injection attacks

**Reference Handling**:
- Verification of all external URLs before inclusion
- Proper formatting to prevent XSS in reports
- Sanitization of all user-provided content

## Conclusion

The vendor risk analysis system represents a sophisticated multi-agent architecture designed for comprehensive vendor assessments. By combining specialized agents, advanced tools, and robust backend services, the system delivers thorough, evidence-based assessments with professional reporting capabilities.

Key strengths of the architecture include:

1. **Specialized Agent Roles**: The separation between the orchestrator and researcher agents allows each to excel at their specific tasks, with models optimized for their particular requirements.

2. **Comprehensive Tool Suite**: The system's specialized tools for web scraping, question management, and PDF generation provide powerful capabilities at each stage of the assessment process.

3. **Structured Workflow**: The step-by-step workflow with explicit user confirmation ensures thorough assessments while maintaining user control throughout the process.

4. **Evidence-Based Research**: The researcher agent's advanced capabilities ensure that all findings are properly sourced and cited, providing trustworthy assessments.

5. **Professional Reporting**: The sophisticated PDF generation pipeline creates beautiful, professional reports with proper formatting and clickable references.

6. **Cloud Integration**: Google Cloud Storage integration ensures reports are easily accessible and shareable across the organization.

This architecture provides a powerful foundation for vendor risk assessment that can be extended and enhanced as requirements evolve. The modular design allows for easy addition of new capabilities, while the structured workflow ensures consistent, high-quality assessments.
