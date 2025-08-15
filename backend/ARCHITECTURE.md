# Backend Architecture: Service-Oriented Design

This document outlines the service-oriented architecture (SOA) for the Privacy Data Governance Graph backend. The design centralizes core business logic into a reusable service, which is then exposed through multiple, independent Cloud Functions acting as transport layers.

## 1. Core Components

The backend is composed of four main components:

### a. `DataGraphService`
- **Location**: `backend/services/data_graph_service.py`
- **Description**: This is the heart of the backend. It is a Python class that encapsulates all business logic for interacting with Google Cloud Spanner and Vertex AI.
- **Responsibilities**:
    - Managing connections to Spanner and the Secret Manager.
    - Initializing the Vertex AI client.
    - **Document Ingestion**: Parsing documents, extracting graph data using an LLM, and populating the Spanner database.
    - **Question Answering**: Interpreting a user's natural language question, performing the necessary graph traversals on Spanner, and synthesizing a coherent answer using an LLM.

### b. `ingest_function`
- **Location**: `backend/ingest_function/`
- **Description**: A Google Cloud Function with an HTTP trigger that handles data ingestion requests.
- **Functionality**: Acts as a thin wrapper around the `DataGraphService`. It receives a document (e.g., via a file upload), passes the content to `data_graph_service.ingest_document()`, and returns the result.

### c. `query_function`
- **Location**: `backend/query_function/`
- **Description**: A Google Cloud Function with an HTTP trigger that handles user queries.
- **Functionality**: A thin wrapper that receives a JSON payload with a "question", passes it to `data_graph_service.answer_question()`, and returns the LLM-generated answer.

### d. `data_graph_mcp_server`
- **Location**: `backend/data_graph_mcp_server/`
- **Description**: A Google Cloud Function that exposes the backend logic via the Model Context Protocol (MCP).
- **Functionality**: Uses `FastAPI` and `FastMCP` to expose methods from the `DataGraphService` as callable "tools" for other LLM agents. The `mangum` library serves as an adapter to make the FastAPI (ASGI) application compatible with the GCF (WSGI) environment.

## 2. Data & Logic Flow

### Ingestion Flow
1.  A client sends a `POST` request with a document to the `ingest_function` URL.
2.  The `ingest_function` calls `DataGraphService.ingest_document()`.
3.  The service uses Vertex AI to extract entities and relationships from the document text.
4.  The service writes the extracted graph data to the Spanner tables.
5.  A success or error response is returned to the client.

### Query Flow
1.  A client (UI or other service) sends a `POST` request with a JSON question to the `query_function` URL.
2.  The `query_function` calls `DataGraphService.answer_question()`.
3.  The service uses an LLM to understand the user's intent and identify key entities.
4.  It queries Spanner to retrieve relevant graph context (nodes and edges).
5.  The context is passed back to the LLM, which synthesizes a natural language answer.
6.  The answer is returned to the client.

## 3. Deployment

Each function (`ingest_function`, `query_function`, `data_graph_mcp_server`) is deployed as a separate, independent Google Cloud service. The ingest and query functions are deployed as Cloud Functions, while the MCP server is deployed as a Cloud Run service. Each has its own `main.py` entry point and `requirements.txt` file, ensuring clean dependency management and isolated scaling.
