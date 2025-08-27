# Simplified Multi-Agent Architecture for Data Graph System

This document provides an overview of the simplified multi-agent architecture for the data graph system, which has been designed to improve maintainability and focus while maintaining robust functionality.

## Architecture Overview

The data graph multi-agent system now consists of two specialized agents orchestrated by a sequential workflow agent:

```
DataGraphWorkflow (SequentialAgent)
├── 1. DocumentAnalysisAgent
└── 2. GraphConstructionAgent
```

## Sub-Agent Responsibilities

### 1. Document Analysis Agent
- **Primary Focus**: Document parsing, content analysis, and basic entity identification
- **Key Responsibilities**:
  - Retrieve document content using `scrape_and_extract_policy_data` tool
  - Collect metadata using restricted metadata-only MCP tools
  - Analyze the parsed content to extract key information
  - Identify data elements, subject types, assets, vendors, etc.
  - Match entities with appropriate entity types using metadata
  - Match data elements with system-seeded data elements
  - Match subject types with system-seeded subject types
  - Present a simple summary of findings grouped by entity type
  - Pass structured analysis to Graph Construction Agent

### 2. Graph Construction Agent
- **Primary Focus**: Graph construction, entity creation, and relationship mapping
- **Key Responsibilities**:
  - Process entities from Document Analysis Agent results
  - Check for similar entities using full MCP toolset
  - Create new entities or use existing ones based on user confirmation
  - Validate relationships against the ontology
  - Create relationships with user confirmation
  - Provide summary of the constructed graph

## Key Benefits

1. **Reduced Cognitive Load**: Each agent has a narrowly defined responsibility
2. **Improved Debugging**: Issues can be isolated to specific stages
3. **Enhanced User Experience**: More granular confirmation points
4. **Better Specialization**: Each agent optimized for its specific task
5. **Increased Reliability**: Validation occurs at multiple stages
6. **Maintainability**: Easier to update individual components

## Design Principles

- **Strict Metadata-Driven Validation**: All entities and relationships validated against MCP metadata
- **User Confirmation Workflow**: Explicit wait points before proceeding to next steps
- **Business-Friendly Presentation**: Technical details hidden from user interfaces
- **Similarity Matching Integrity**: Only show similar entities returned by MCP tools
- **Sequential Processing**: Clear, predictable workflow with state passing between agents
- **Direct Metadata Tool Access**: Coordinator agent has direct access to metadata tools

## MCP Tool Integration

The system uses a specialized approach to ensure proper MCP tool integration:

### Metadata Tool Filtering

1. **Filtered Metadata Toolset**: The Document Analysis agent has access to a restricted set of metadata-only MCP tools:
   ```python
   metadata_mcp_toolset = MCPToolset(
       connection_params=StreamableHTTPConnectionParams(
           url=configs.MCP_SERVER_URL,
           headers={
               "Content-Type": "application/json",
               "Accept": "text/event-stream"
           },
           timeout=30
       ),
       # Only include metadata-related tools
       tool_allow_list=[
           "get_entity_types",
           "get_entity_parameters",
           "get_relationship_ontology",
           "list_data_elements",
           "list_data_subject_types"
       ]
   )
   ```

2. **Full MCP Toolset**: The Graph Construction agent has access to the complete MCP toolset for entity and relationship creation:
   ```python
   # Graph Construction agent uses the full MCP toolset
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
   ```

3. **Explicit Tool Usage Instructions**: The Document Analysis agent prompt explicitly restricts tool usage:
   ```
   RESTRICTED TOOL USAGE - ONLY USE THESE TOOLS:
   - scrape_and_extract_policy_data - For document retrieval
   - get_entity_types - For entity type metadata
   - get_entity_parameters - For entity parameters
   - get_relationship_ontology - For relationship types
   - list_data_elements - For system data elements
   - list_data_subject_types - For system subject types
   
   DO NOT use any other MCP tools like create_*, update_*, delete_*, or other list_* tools.
   ```

This architecture ensures that metadata tools are properly called and their outputs are available for entity classification, resolution, and relationship mapping.

This enhanced architecture maintains all existing requirements while providing a more robust and specialized workflow for privacy policy analysis and data graph construction.
