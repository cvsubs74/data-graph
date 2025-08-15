# **Turnkey Serverless Graph RAG Application on Google Cloud**

## **1. Project Overview**

This project provides a complete, production-grade, serverless Graph RAG (Retrieval-Augmented Generation) web application deployed on Google Cloud. It consists of a React frontend and a backend powered by Cloud Run services and Cloud Functions. The application allows users to upload text documents, which are then processed to extract a knowledge graph of entities and relationships. This graph is stored in Google Cloud Spanner. Users can then ask questions, and the system will retrieve relevant information from the graph to generate an answer using Vertex AI's Gemini model.

---

## **2. Architecture Diagram**

A text-based representation of the application architecture:

```
[User's Browser]
      |
      | (HTTPS Requests)
      v
[React Frontend (Vite)]
      |         |
(1) Upload  (2) Query
      |         |
      v         v
[GCP Cloud Function: ingest-function]   [GCP Cloud Run: mcp-server]
      |         |           |
      | (Extracts Graph)  (CRUD Operations)  (MCP Tools)
      v         |           |
[Vertex AI Gemini 2.5 Flash Lite]  |
      |         |
      | (Stores Graph)    |
      v         v
[Google Cloud Spanner]
  - rag-instance
  - rag-db
    - Assets Table
    - ProcessingActivities Table
    - DataElements Table
    - EntityRelationships Table

[Google Secret Manager]
  - spanner-instance-id
  - spanner-database-id
```

---

## **3. GCP Setup Instructions**

Follow these steps to configure your Google Cloud environment. Run these commands from your local terminal where the `gcloud` SDK is authenticated.

### **Step 3.1: Create & Configure Google Cloud Project**

First, you need a Google Cloud project. If you don't have one, create it and link it to a billing account.

```bash
# 1. Create a new project (replace YOUR_PROJECT_ID with a unique ID)
gcloud projects create graph-rag-app-20250811 --name="Graph RAG Project"

# 2. Set the project for the current gcloud session
gcloud config set project graph-rag-app-20250811

# 3. Link billing to the project automatically
# This command finds the first active billing account and links it to your project.
BILLING_ACCOUNT=$(gcloud beta billing accounts list --filter='open=true' --format='value(name)' --limit=1)
if [ -z "$BILLING_ACCOUNT" ]; then
  echo "No active billing account found. Please go to the GCP Console to set up a billing account."
else
  echo "Found billing account: $BILLING_ACCOUNT"
  gcloud beta billing projects link graph-rag-app-20250811 --billing-account=$(basename $BILLING_ACCOUNT)
fi
```

### **Step 3.2: Enable Required APIs**

```bash
gcloud services enable \
  run.googleapis.com \
  iam.googleapis.com \
  secretmanager.googleapis.com \
  spanner.googleapis.com \
  aiplatform.googleapis.com \
  cloudfunctions.googleapis.com
```

### **Step 3.3: Create Spanner Instance and Database**

```bash
# Create the Spanner instance
gcloud spanner instances create rag-instance \
  --config=regional-us-west1 \
  --description="RAG Spanner Instance" \
  --nodes=1

# Create the database

**Note:** The following command creates a new database with the complete schema. If you have an existing database, you will need to delete it first, as this schema is a complete replacement of the old one.

```bash
gcloud spanner databases ddl update rag-db \
  --instance=rag-instance \
  --ddl="
    -- DDL for Privacy Data Graph

    -- Entity Tables

    CREATE TABLE Assets (
        asset_id STRING(36) NOT NULL,
        name STRING(256) NOT NULL,
        description STRING(MAX),
        properties JSON,
        created_at TIMESTAMP NOT NULL OPTIONS(allow_commit_timestamp=true),
        updated_at TIMESTAMP NOT NULL OPTIONS(allow_commit_timestamp=true)
    ) PRIMARY KEY (asset_id);

    CREATE INDEX AssetsByName ON Assets(name);

    CREATE TABLE ProcessingActivities (
        activity_id STRING(36) NOT NULL,
        name STRING(256) NOT NULL,
        description STRING(MAX),
        properties JSON,
        created_at TIMESTAMP NOT NULL OPTIONS(allow_commit_timestamp=true),
        updated_at TIMESTAMP NOT NULL OPTIONS(allow_commit_timestamp=true)
    ) PRIMARY KEY (activity_id);

    CREATE INDEX ProcessingActivitiesByName ON ProcessingActivities(name);

    CREATE TABLE DataElements (
        element_id STRING(36) NOT NULL,
        name STRING(256) NOT NULL,
        description STRING(MAX),
        properties JSON,
        created_at TIMESTAMP NOT NULL OPTIONS(allow_commit_timestamp=true),
        updated_at TIMESTAMP NOT NULL OPTIONS(allow_commit_timestamp=true)
    ) PRIMARY KEY (element_id);

    CREATE INDEX DataElementsByName ON DataElements(name);

    CREATE TABLE DataSubjectTypes (
        subject_id STRING(36) NOT NULL,
        name STRING(256) NOT NULL,
        description STRING(MAX),
        properties JSON,
        created_at TIMESTAMP NOT NULL OPTIONS(allow_commit_timestamp=true),
        updated_at TIMESTAMP NOT NULL OPTIONS(allow_commit_timestamp=true)
    ) PRIMARY KEY (subject_id);

    CREATE INDEX DataSubjectTypesByName ON DataSubjectTypes(name);

    CREATE TABLE Vendors (
        vendor_id STRING(36) NOT NULL,
        name STRING(256) NOT NULL,
        description STRING(MAX),
        properties JSON,
        created_at TIMESTAMP NOT NULL OPTIONS(allow_commit_timestamp=true),
        updated_at TIMESTAMP NOT NULL OPTIONS(allow_commit_timestamp=true)
    ) PRIMARY KEY (vendor_id);

    CREATE INDEX VendorsByName ON Vendors(name);

    -- Generic Relationship Table

    CREATE TABLE EntityRelationships (
        source_id STRING(36) NOT NULL,
        target_id STRING(36) NOT NULL,
        relationship_type STRING(128) NOT NULL,
        properties JSON,
        created_at TIMESTAMP NOT NULL OPTIONS(allow_commit_timestamp=true),
        updated_at TIMESTAMP NOT NULL OPTIONS(allow_commit_timestamp=true)
    ) PRIMARY KEY (source_id, target_id, relationship_type);

    CREATE INDEX RelationshipsBySource ON EntityRelationships(source_id);
    CREATE INDEX RelationshipsByTarget ON EntityRelationships(target_id);
" 
```

### **Step 3.4: Create Secrets in Secret Manager**

```bash
# Create or update secrets for Spanner identifiers. This script is idempotent.
gcloud secrets describe spanner-instance-id >/dev/null 2>&1 || \
    gcloud secrets create spanner-instance-id --replication-policy=automatic
echo -n "rag-instance" | gcloud secrets versions add spanner-instance-id --data-file=-

gcloud secrets describe spanner-database-id >/dev/null 2>&1 || \
    gcloud secrets create spanner-database-id --replication-policy=automatic
echo -n "rag-db" | gcloud secrets versions add spanner-database-id --data-file=-

# Grant access to the default compute service account
PROJECT_NUMBER=$(gcloud projects describe $(gcloud config get-value project) --format='value(projectNumber)')
SERVICE_ACCOUNT="${PROJECT_NUMBER}-compute@developer.gserviceaccount.com"

gcloud secrets add-iam-policy-binding spanner-instance-id \
  --member="serviceAccount:${SERVICE_ACCOUNT}" \
  --role="roles/secretmanager.secretAccessor"

gcloud secrets add-iam-policy-binding spanner-database-id \
  --member="serviceAccount:${SERVICE_ACCOUNT}" \
  --role="roles/secretmanager.secretAccessor"
```

---

## **4. Deployment Instructions**

### **Step 4.1: Deploy Backend Components**

The easiest way to deploy all backend components is to use the provided deployment script:

```bash
./deploy.sh
```

This script will deploy both the `ingest-function` Cloud Function and the `mcp-server` Cloud Run service with all necessary configurations.

If you prefer to deploy manually, you can use the following commands:

**`ingest-function`:**
```bash
cd backend/ingest-function

gcloud functions deploy ingest-function \
  --gen2 \
  --runtime=python311 \
  --region=us-central1 \
  --source=. \
  --entry-point=ingest_document \
  --trigger-http \
  --allow-unauthenticated \
  --memory=1Gi \
  --set-env-vars GCP_PROJECT=$(gcloud config get-value project)
```

**`mcp-server`:**
```bash
cd backend/data_graph_mcp_server

gcloud run deploy mcp-server \
  --source=. \
  --platform=managed \
  --region=us-central1 \
  --allow-unauthenticated \
  --set-env-vars GCP_PROJECT=$(gcloud config get-value project)
```

### **Step 4.2: MCP Server Tools**

The MCP server provides a set of tools for CRUD operations on the data graph using the FastMCP framework. These tools include:

* **Asset Management**
  * `create_asset`: Creates a new asset with name, description, and properties
  * `get_asset`: Retrieves an asset by ID
  * `update_asset`: Updates an existing asset
  * `delete_asset`: Deletes an asset
  * `list_assets`: Lists all assets

* **Processing Activity Management**
  * `create_processing_activity`: Creates a new processing activity
  * `get_processing_activity`: Retrieves a processing activity by ID
  * `list_processing_activities`: Lists all processing activities
  * `delete_processing_activity`: Deletes a processing activity

* **Data Element Management**
  * `create_data_element`: Creates a new data element
  * `get_data_element`: Retrieves a data element by ID
  * `list_data_elements`: Lists all data elements
  * `delete_data_element`: Deletes a data element

* **Relationship Management**
  * `create_relationship`: Creates a relationship between two entities
  * `get_relationships`: Retrieves relationships for an entity
  * `delete_relationship`: Deletes a relationship

All properties passed to these tools are serialized as JSON strings before being stored in Spanner to ensure compatibility with the database schema.

### **Step 4.3: Configure and Run the Frontend**

1.  **Navigate to the frontend directory:**
    ```bash
    cd frontend
    ```

2.  **Create a local environment file:**
    Copy the provided `.env` template to a new `.env.local` file.
    ```bash
    cp .env .env.local
    ```

3.  **Update API URLs:**
    Open `.env.local` and replace the placeholder URLs with the trigger URLs from your deployed Cloud Functions.

4.  **Install dependencies and run the development server:**
    ```bash
    npm install
    npm run dev
    ```

---

## **5. Usage Instructions**

1.  Open the local development URL provided by `npm run dev` in your browser.
2.  Use the "Upload Document" section to select and upload a `.txt` file.
3.  Once the upload is successful, use the "Ask a Question" section to query the knowledge graph.

---

## **6. Troubleshooting**

*   **CORS Errors**: If the frontend cannot reach the backend, you may need to configure CORS on your Cloud Functions. This typically involves modifying the Python code to include CORS headers (e.g., using the `flask-cors` library).
*   **IAM Permissions**: If you see `PermissionDenied` errors, ensure the service account used by your Cloud Functions has the `roles/secretmanager.secretAccessor` and `roles/spanner.databaseUser` roles.
