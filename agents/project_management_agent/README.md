# Project Management Agent System Architecture

## Introduction

This document outlines the implementation of the project management agent system for privacy governance. The architecture uses a multi-agent pattern with an orchestrator agent that guides the user through the project analysis process while leveraging specialized sub-agents for specific tasks.

## System Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────────┐
│                                                                         │
│                      PROJECT MANAGEMENT SYSTEM                          │
│                                                                         │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  ┌───────────────────────────────────────────────────────────────────┐  │
│  │                                                                   │  │
│  │                 Project Management Orchestrator                   │  │
│  │                      (Main Agent)                                 │  │
│  │                                                                   │  │
│  └───────────────────────────────────────────────────────────────────┘  │
│                │                  │                 │                   │
│                ▼                  ▼                 ▼                   │
│  ┌─────────────────────┐  ┌─────────────────┐  ┌───────────────────┐   │
│  │                     │  │                 │  │                   │   │
│  │ Document Parser     │  │ Entity Detector │  │ Project Analyzer  │   │
│  │ Agent (As Tool)     │  │ Agent (As Tool) │  │ Agent (As Tool)   │   │
│  │                     │  │                 │  │                   │   │
│  └─────────────────────┘  └─────────────────┘  └───────────────────┘   │
│                                                                         │
├─────────────────────────────────────────────────────────────────────────┤
│                           BACKEND SERVICES                              │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  ┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐   │
│  │                 │     │                 │     │                 │   │
│  │  Document       │     │  Data Graph     │     │ Entity Type     │   │
│  │  Scraper Tool   │     │  MCP Server     │     │ Registry        │   │
│  │                 │     │                 │     │                 │   │
│  └─────────────────┘     └─────────────────┘     └─────────────────┘   │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

## Implementation Architecture

The implementation uses a multi-agent architecture with a main orchestrator agent that guides the user through the entire project management process. This agent leverages specialized sub-agents as tools to perform specific tasks.

### Code Structure

The project follows a modular architecture with clear separation of concerns:

```
├── agent.py           # Defines the root_agent and specialized agents as tools
├── main.py            # Entry point that imports root_agent and handles server/CLI execution
├── config.py          # Configuration settings for the agent system
├── prompts.py         # Agent instructions and prompts
├── document_parser.py # Document parsing functionality
├── entity_detector.py # Entity detection functionality
├── project_analyzer.py # Project analysis functionality
└── tools/
    ├── __init__.py    # Tool exports
    └── tools.py       # Tool implementations
```

### 1. Project Management Orchestrator (Main Agent)

**Purpose**: Guide the user through the complete project management process from start to finish.

**Implementation**: Defined as `root_agent` in agent.py and used by main.py.

**Responsibilities**:
- Introduce itself and explain capabilities upon launch
- Guide the user through a structured workflow with explicit confirmation at each step
- Coordinate the use of specialized sub-agents as tools for different phases
- Synthesize information into a comprehensive project analysis
- Ensure proper entity detection and classification throughout the process

**Workflow Sequence**:
1. **Document Parsing**: Use document parser agent to analyze uploaded documents
2. **Entity Detection**: Use entity detector agent to identify entities in the documents
3. **Project Analysis**: Use project analyzer agent to analyze the project context
4. **Report Generation**: Compile findings into a comprehensive project report
5. **Final Confirmation**: Ask for user feedback on the report

**Tools Used**:
- Document parser agent (as a tool)
- Entity detector agent (as a tool)
- Project analyzer agent (as a tool)
- MCP toolset for entity management

### 2. Document Parser Agent (Specialist Sub-Agent)

**Purpose**: Parse and analyze uploaded documents to extract structured content.

**Responsibilities**:
- Process document content from various formats
- Extract text and structure from documents
- Identify document sections and key information
- Prepare content for entity detection
- Provide a summary of document structure and content

**Input**:
- Document URL or raw content

**Output**:
- Structured document content
- Document summary
- Preliminary entity candidates

### 3. Entity Detector Agent (Specialist Sub-Agent)

**Purpose**: Identify and classify entities within parsed documents.

**Responsibilities**:
- Analyze parsed document content
- Identify potential entities based on context
- Classify entities using MCP entity type registry
- Match entities with existing entities in the system
- Provide a list of detected entities with confidence scores

**Input**:
- Parsed document content from Document Parser Agent

**Output**:
- List of detected entities with classifications
- Entity relationships and context
- Confidence scores for entity detection

### 4. Project Analyzer Agent (Specialist Sub-Agent)

**Purpose**: Analyze the project context and provide insights based on detected entities.

**Responsibilities**:
- Analyze the project based on detected entities
- Identify project risks and compliance issues
- Generate recommendations for project management
- Create a comprehensive project analysis report
- Provide actionable insights for privacy governance

**Input**:
- Detected entities from Entity Detector Agent
- Project context information

**Output**:
- Project analysis report
- Risk assessment
- Compliance recommendations
- Privacy governance insights

## Backend Services

The system relies on several backend services and tools to perform its functions:

### 1. Document Scraper Tool

**Purpose**: Extract and analyze content from documents.

**Functionality**:
- Scrapes content from provided URLs or document files
- Extracts text and structure from documents
- Validates that the document is legitimate and processable

### 2. Data Graph MCP Server

**Purpose**: Provide access to entity types, project metadata, and other MCP services.

**Functionality**:
- Retrieves entity types and definitions
- Manages project metadata
- Provides entity relationship ontology
- Handles entity creation and management

The project management agent uses the same data graph MCP server as the data graph agent, leveraging its existing entity types, relationships, and data management capabilities.

## Implementation Considerations

### User Interaction and Confirmation

The system is designed with explicit user confirmation at key decision points:

1. **After Document Parsing**: The user must confirm before proceeding to entity detection
2. **After Entity Detection**: The user can review, add, remove, or modify detected entities
3. **After Project Analysis**: The user can request revisions to the analysis

### Entity Detection Requirements

The system enforces strict entity detection standards:

- Entities must be matched with defined entity types
- Entity detection must provide confidence scores
- Entity relationships must follow the defined ontology
- Entity detection must be explainable and transparent

### Automatic Report Generation

The system automatically generates a comprehensive report after analysis is completed:

- Executive Summary
- Project Overview
- Entity Analysis
- Risk Assessment
- Compliance Recommendations
- Privacy Governance Insights
- References and Sources

## Installation and Setup

### Prerequisites

- Python 3.10 or higher
- Google ADK CLI installed
- Access to Google Cloud Platform (for deployment)
- Access to the Data Graph MCP Server

### Local Development Setup

1. **Clone the repository**

```bash
git clone <repository-url>
cd graphrag/agents/project_management_agent
```

2. **Create and activate a virtual environment**

```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. **Install dependencies**

```bash
pip install -r requirements.txt
```

4. **Configure environment variables**

Create a `.env` file in the project directory with the following variables:

```
MCP_SERVER_URL=https://data-graph-mcp-server-79797180773.us-central1.run.app/mcp
GCP_PROJECT=graph-rag-app-20250811
CLOUD_LOCATION=us-central1
```

### Running the Agent Locally

To run the agent locally with the ADK web interface:

```bash
adk web
```

This will start the agent on http://localhost:8000 by default.

## Deployment

### Deploying to Google Cloud Run

The project includes a deployment script for Google Cloud Run:

```bash
./deploy_to_cloud_run.sh
```

This script will:
1. Authenticate with Google Cloud
2. Set the project ID
3. Deploy the agent to Cloud Run with a web UI

You can customize the deployment by modifying the variables at the top of the script:

```bash
PROJECT_ID=your-project-id
REGION=your-preferred-region
SERVICE_NAME=your-service-name
```

## MCP Server Configuration

The project management agent relies on the Data Graph MCP Server for entity management. The MCP server provides the following tools:

- `get_entity_types`: Retrieves available entity types from the registry
- `get_entity_parameters`: Gets parameters for specific entity types
- `find_similar_entities`: Searches for similar entities in the system
- `get_relationship_ontology`: Retrieves the relationship ontology for entities

The MCP server URL is configured in `tools/tools.py` and should point to:

```
https://data-graph-mcp-server-79797180773.us-central1.run.app/mcp
```

## Usage Examples

### Processing a Document URL

1. Start the agent with `adk web`
2. In the web interface, provide a document URL:
   ```
   I'd like to analyze this privacy policy: https://example.com/privacy-policy
   ```
3. The Document Parser Agent will extract and analyze the content
4. Review the parsed document and confirm to proceed
5. The Entity Detector Agent will identify entities in the document
6. Review the detected entities and confirm to proceed
7. The Project Analyzer Agent will provide a comprehensive analysis

### Analyzing Existing Entities

1. Start the agent with `adk web`
2. Request an analysis of existing entities:
   ```
   I'd like to analyze the privacy implications of our current data processing activities
   ```
3. The agent will guide you through the process of selecting entities to analyze
4. The Project Analyzer Agent will provide insights and recommendations

## Troubleshooting

### Common Issues

1. **MCP Server Connection Errors**
   - Verify the MCP server URL in `tools/tools.py`
   - Check network connectivity to the MCP server

2. **Entity Detection Issues**
   - Ensure the document is properly parsed before entity detection
   - Verify that the entity types are available in the MCP server

3. **Deployment Failures**
   - Check Google Cloud authentication
   - Verify project ID and region settings
   - Ensure the ADK CLI is properly installed

## Conclusion

The project management agent system uses a multi-agent architecture with specialized sub-agents to provide a comprehensive solution for privacy governance project management. This approach provides a streamlined user experience while maintaining the thoroughness and reliability needed for effective project management in the context of privacy governance.
