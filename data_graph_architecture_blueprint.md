# Data Graph Multi-Agent Architecture Blueprint

## Executive Summary

The Data Graph Multi-Agent system implements a sophisticated architecture for privacy policy analysis and data graph construction. The system employs specialized agents, metadata-driven validation, user confirmation workflows, and semantic similarity search to create a robust, trustworthy, and user-friendly privacy data governance solution.

## Core Architectural Patterns

### 1. Specialized Agent Roles & Responsibilities

The architecture employs a clear separation of concerns through specialized agents:

* **Document Analysis Agent**: 
  - Extracts structured data from privacy policies
  - Uses scraping tools for raw text extraction
  - Performs silent metadata collection using MCP tools
  - Classifies entities using descriptions from entity type metadata
  - Presents findings without technical details (no similarity scores)
  - Waits for user confirmation before proceeding

* **Graph Construction Agent**:
  - Takes structured data from the Document Analysis Agent
  - Builds and validates the data graph
  - Processes entities one at a time with user confirmation
  - Validates relationships against the ontology
  - Ensures all entities and relationships conform to system metadata

### 2. Sequential Orchestration Pattern

The architecture implements a sequential orchestration pattern through the `SequentialAgent` class:

* **Fixed Execution Order**: Agents execute in a predetermined sequence
* **State Passing**: Document Analysis Agent saves output to session state for Graph Construction Agent
* **Single Entry Point**: Root agent provides a unified interface to the multi-agent system
* **Shared Global Context**: Both agents operate under the same global instruction

### 3. MCP Tooling Pattern

The MCP server implements a comprehensive tooling pattern:

* **Metadata-Driven Validation**: Tools provide metadata for entity types, parameters, and relationship ontology
* **CRUD Operations**: Complete set of tools for entities and relationships
* **Semantic Search**: Vector embedding-based similarity search
* **Consistent Error Handling**: Robust error handling and logging
* **Transactional Integrity**: Database operations executed within transactions

### 4. User Confirmation Workflow

A key architectural pattern ensuring trust and accuracy:

* **Staged Presentation**: Findings and proposed actions presented before execution
* **Explicit Wait Points**: Agents pause for user confirmation at critical steps
* **Business-Friendly Format**: Technical details hidden from users
* **Incremental Processing**: Entities processed one at a time with confirmation for each
* **Transparent Options**: Similar entities presented clearly to avoid duplication

### 5. Vector Embedding Similarity Search Pattern

Sophisticated entity matching and deduplication:

* **Gemini Embedding Model**: Google's Vertex AI for semantic embeddings
* **Cosine Similarity**: Finding semantically similar entities
* **Embedding Storage**: Embeddings stored in Spanner database
* **Automatic Recalculation**: Embeddings updated when entities change
* **Abstracted Presentation**: Similarity scores hidden from users
* **Strict System Boundaries**: Only searches within existing system data

## Technical Implementation

### Database Architecture

* **Google Cloud Spanner**: Highly available, globally distributed database
* **Entity Tables**: Assets, Vendors, ProcessingActivities, DataElements, DataSubjectTypes
* **Relationship Table**: EntityRelationships for graph connections
* **Metadata Tables**: EntityTypes, EntityTypeProperties, RelationshipOntology

### Cloud Infrastructure

* **Google Cloud Run**: Serverless deployment for agents
* **Vertex AI**: Gemini embedding model for semantic similarity
* **Secret Manager**: Secure credential management
* **Docker Containers**: Consistent deployment environment

### Error Handling & Reliability

* **Transactional Operations**: Ensuring data consistency
* **Comprehensive Logging**: Tracking agent and server operations
* **Exception Management**: Graceful error handling throughout
* **User Confirmation**: Preventing erroneous data entry

## Key Strengths & Benefits

1. **Trustworthy Operation**: User confirmation at critical steps ensures accuracy
2. **Metadata-Driven Validation**: Prevents invalid entities and relationships
3. **Business-Friendly Interface**: Technical details abstracted away
4. **Modular Architecture**: Specialized agents with clear responsibilities
5. **Semantic Intelligence**: Vector embeddings for intelligent entity matching
6. **Robust Data Integrity**: Transactional operations and relationship validation

## Future Enhancement Opportunities

1. **Parallel Agent Processing**: For non-sequential tasks
2. **Enhanced Visualization**: Graph visualization tools for data exploration
3. **Automated Testing**: Test suite for agent behavior validation
4. **Feedback Loop Integration**: Learning from user corrections
5. **Extended Entity Types**: Supporting additional privacy data concepts
