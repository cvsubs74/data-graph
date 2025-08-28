# A Tool-Centric Agentic Blueprint for Privacy Governance

## Introduction: Architecture as a Consequence, Not a Goal

This document outlines a blueprint for an agentic system designed specifically for the complex domain of **privacy policy analysis and data graph construction**. It's crucial to understand that the agentic architecture presented here is not an abstract framework; it is a direct consequence of the problem's unique challenges. The primary goal is not simply to "build agents," but to create a transparent, verifiable, and user-centric system for navigating the nuanced and high-stakes world of data privacy.

The core principle is **domain-first design**. The architecture serves the task, not the other way around. To illustrate why a single, context-rich agent approach was chosen, we will contrast it with a multi-agent framework, demonstrating how a continuous, stateful session is essential for achieving trustworthiness and accuracy in this domain.

---

## Architectural Philosophy: The Case for a Unified Dialogue

In a domain as sensitive as privacy compliance, creating an accurate and comprehensive data map is paramount. Today, OneTrust tackles this with **static assessment templates**. This approach provides structure by defining a fixed set of questions upfront to capture information about entities and their attributes. However, this rigidity means the process cannot dynamically adapt to the specific language of a legal document or to evolving business needs. A template is a fixed script, not an intelligent conversation.

Therefore, our philosophy is rooted in creating a **single, intelligent agent** that transforms this process from a static checklist into a dynamic, context-aware dialogue. This unified agent empowers the user in a seamless, stateful workflow, ensuring that no information is lost and that the user can interject with questions at any point.

The difference is best explained with an analogy:
* The **static template approach** is like giving a builder a generic, one-size-fits-all blueprint and a rigid checklist. They can only build what's on the plan and ask the questions on the list, regardless of the unique conditions of the construction site.
* The **multi-agent approach** is like hiring a disconnected team. The architect agent draws a plan, leaves it on the desk, and goes home. The construction agent picks it up, but if they have a question about the architect's intent, they can't ask—the architect is gone. This handoff is where context is lost.
* The **single-agent approach** is like working directly with a master builder. This expert reads the terrain (the privacy policy), creates a plan, and then works with you to execute it. If you ask a question about the initial plan while they're laying the foundation, they have the full context to answer you and then seamlessly resume their work. The conversation is continuous and context-rich.

This single-agent method makes the entire process dynamic and intelligent, adapting itself to the document and the user's needs rather than forcing the complexities into a fragmented, unreliable workflow.

---

## Architectural Choice: Multi-Agent Relay vs. Single-Agent Session

The most critical design decision is how to structure the agentic workflow. While a multi-agent system might seem appealing for separating concerns, it introduces significant reliability issues. For complex, multi-step tasks that require user interaction, the single-agent approach offers a vastly superior, context-rich session.

The multi-agent framework is **unreliable because it acts as a relay**. Once the first agent is done, it generates a response and passes it to the next one, often losing the nuance and history of the user interaction. With a single LLM Agent, the session is context-rich, and the user can ask any question at any point without losing context on the data graph construction process.

### Key Differences at a Glance

| Aspect | Multi-Agent Approach (Unreliable Relay) | Single-Agent Approach (Context-Rich Session) |
| :--- | :--- | :--- |
| **Architecture** | A `SequentialAgent` orchestrating multiple `LlmAgent`s. Context is passed between them. | A single `LlmAgent` responsible for the entire end-to-end process. |
| **User Experience** | Fragmented and brittle. The user is in a session with one agent, which then ends and passes a summary to the next. The user cannot easily refer back to earlier parts of the conversation. | Seamless and robust. The user maintains a continuous dialogue with one agent that has access to the full conversational history. |
| **Context Handling** | **High risk of context loss.** Each agent handoff is a potential point of failure where information is dropped or misinterpreted. The system acts as a "relay," quickly losing context. | **Context is preserved.** The LLM tracks the entire workflow, allowing the user to ask clarifying questions about previous steps without derailing the process. |
| **Maintainability** | Difficult to debug. A failure could be due to a misinterpretation in the handoff *between* agents, not just within a single prompt. | Easier to debug. The entire interaction exists in a single, continuous log, making it simple to trace the source of an error. |

### Demos
Single Agent: https://data-graph-agent-79797180773.us-central1.run.app

Multi Agent: https://data-graph-multi-agent-79797180773.us-central1.run.app

### Deeper Dive: A Tale of Two Workflows

Imagine a scenario where a user is interacting with an agent to add a new vendor based on a document analysis.

* With the **multi-agent pipeline**, the `DocumentAnalysisAgent` first talks to the user, identifies the vendor, and asks some initial questions. It then finishes its job and passes a summary (e.g., "Create vendor: PaySecure, contact: none") to the `GraphConstructionAgent`. If the user then asks, "Wait, what did the document say about their security practices again?", the `GraphConstructionAgent` is helpless. It has no access to the previous conversation or the initial analysis. It only received a simple instruction. This is the core failure of the relay model.
* With the **single agent**, the entire interaction is one continuous session. When the agent is ready to create the vendor, it might say, "I need a contact email for PaySecure." The user can then ask, "What did the document say about their security practices again?" The agent, having the full context, can answer that question and then seamlessly return to its previous state: "Good question. The document did not mention their security practices. Now, about that contact email for PaySecure?" The session remains rich and the workflow is uninterrupted.

---

## The MCP Toolbox: The System's External Brain 🧠

The foundation of this architecture is the **MCP (Master Control Program) Server Toolbox**. It acts as the system's external brain, providing the LLM with all the context, rules, and intelligent functions it needs. This knowledge is seeded directly into the database, creating a single source of truth that the agent accesses through tools.

### The Anatomy of the System's Knowledge

The agent's understanding of the privacy domain is built from four key pillars of metadata, all defined in the system:

**1. The Core Concepts (Entity Types)**
Before parsing a document, the agent calls **`get_entity_types()`** to learn what it should be looking for. The system defines five core concepts:
* **Asset**: A system, application, or database.
* **ProcessingActivity**: A business process that uses data.
* **DataElement**: A specific category of personal data.
* **DataSubjectType**: A category of individual.
* **Vendor**: A third-party company or service.

**2. The Required Information (Entity Properties)**
The agent calls **`get_entity_parameters()`** to learn what specific attributes are needed for each entity type, including whether they are mandatory. This is what drives the dynamic conversation.
* For an **Asset**:
    * `hosting_location` (String, **Required**): The physical or cloud region where the asset is hosted.
    * `data_retention_days` (Integer, *Optional*): Number of days data is retained in this asset.
* For a **Vendor**:
    * `contact_email` (String, **Required**): The primary contact email for the vendor.
    * `dpa_signed` (Boolean, *Optional*): Indicates if a Data Processing Agreement is signed.
* For a **DataElement**:
    * `sensitivity_level` (String, **Required**): The sensitivity level of the data (e.g., Public, Confidential, Secret).

**3. The Pre-Seeded Vocabulary (System Data)**
To ensure consistency, the system is pre-loaded with a standardized list of common Data Elements and Data Subject Types. The agent uses **`find_similar_entities()`** to match terms from a policy to this official vocabulary.
* **Pre-seeded Data Elements include**: 'Email Address', 'Full Name', 'IP Address', 'Payment Information', 'Device ID', etc.
* **Pre-seeded Data Subject Types include**: 'Customer', 'Employee', 'Vendor Contact', 'Job Applicant'.

**4. The Rules of Engagement (Relationship Ontology)**
This is the most critical metadata, defining the valid ways entities can be connected. The agent calls **`get_relationship_ontology()`** and learns the following set of ironclad rules:
* `ProcessingActivity` **USES** `Asset`
* `Asset` **CONTAINS** `DataElement`
* `Asset` **CONTAINS** `DataSubjectType`
* `Asset` **TRANSFERS_DATA_TO** `Vendor`
* `ProcessingActivity` **ASSISTED_BY** `Vendor`

### The Power of Embeddings: Enabling Semantic Search

A core principle of the database design is the inclusion of a vector embedding in every primary entity record. As seen in the DDL, each key table (`Assets`, `Vendors`, `ProcessingActivities`, etc.) contains an **`embedding ARRAY<FLOAT64>`** column. This is the engine that powers the system's semantic intelligence.

**Why it matters:** Privacy policies use varied language. A document might mention a "payment processor," "billing partner," or "credit card handler." A simple keyword search would see these as three different things. Vector embeddings allow the system to understand that these phrases are **semantically related** because their meanings are conceptually close.

**How it works:**
1.  When a new entity like a Vendor is created, its name and description are converted into a numerical vector by an embedding model.
2.  This vector is stored in the `embedding` column for that record.
3.  When the agent later encounters a new term (e.g., "billing partner") and calls the **`find_similar_entities()`** tool, the tool generates a vector for this new term.
4.  It then performs a high-speed vector similarity search (like cosine similarity) against all the stored embeddings in the database to find the closest conceptual matches, enabling intelligent de-duplication.

This is the difference between searching a library for a book by its exact title versus asking a librarian for "books *about* artificial intelligence," who can then find relevant books with many different titles.

## Vector Representations: Tool-Driven Similarity Detection

### The Challenge of Entity Resolution

One of the most critical challenges in data graph construction is **entity resolution** - determining whether an entity mentioned in a document corresponds to one already in the system. Traditional approaches rely on exact string matching or basic fuzzy matching, which often fail to capture semantic similarities or handle variations in terminology.

For example, a document might mention "customer contact details" while the system has a data element called "customer personal information." These refer to the same concept but use different language.

### Vector Embeddings as the Solution

Our architecture addresses this challenge by maintaining **vector representations** (embeddings) of all entities in the system. These dense numerical representations capture the semantic meaning of entities, enabling similarity detection that goes beyond simple string matching.

| Entity Type | Vector Representation Benefits |
| :--- | :--- |
| **Data Elements** | Captures semantic similarities between different terms for the same type of data |
| **Data Subject Types** | Recognizes variations in how people categories are described |
| **Assets** | Identifies systems with similar functions despite naming differences |
| **Processing Activities** | Connects related business processes across different terminology |
| **Vendors** | Matches vendor mentions with existing records despite variations |

### Implementation Strategy

1. **Embedding Generation**: When entities are created or updated in the system, their descriptions and metadata are processed through an embedding model to generate vector representations.

2. **Storage in Database**: These vectors are stored alongside the entities in the database schema, as seen in the `embedding ARRAY<FLOAT64>` fields in our DDL.

3. **Tool-Driven Similarity Search**: The agent delegates all similarity detection to specialized tools rather than attempting to perform matching itself:

```python
def find_similar_entities(entity_type, query_text):
    # Generate embedding for the query text
    query_embedding = embedding_model.encode(query_text)
    
    # Search the database for similar entities using vector similarity
    results = database.search_similar(
        entity_type=entity_type,
        embedding=query_embedding,
        threshold=0.75  # Configurable similarity threshold
    )
    
    return results
```

### Key Benefits of Tool-Driven Similarity

1. **Separation of Concerns**: The LLM focuses on understanding the document and extracting potential entities, while specialized tools handle the complex task of entity resolution.

2. **Consistency and Reliability**: By externalizing similarity detection to tools, we ensure consistent results that aren't subject to LLM variability or hallucination.

3. **Scalability**: Vector search can efficiently handle large databases of entities, allowing the system to scale as the organization's data graph grows.

4. **Auditability**: All similarity decisions are made by deterministic tools with configurable thresholds, creating a clear audit trail for entity resolution decisions.

5. **Continuous Improvement**: The embedding models and similarity thresholds can be tuned over time based on user feedback without requiring changes to the agent's prompts.

### Example Workflow

1. The agent identifies "customer email addresses" in a document.
2. Instead of guessing whether this matches existing data elements, it calls `find_similar_entities('DataElement', 'customer email addresses')`.
3. The tool returns that "Email Address" is a 92% match.
4. The agent presents this match to the user: "I found that 'customer email addresses' likely refers to the existing data element 'Email Address' in our system."
5. The user confirms or corrects this match, ensuring accuracy.

By leveraging vector representations and tool-driven similarity detection, our architecture ensures that entity resolution is accurate, consistent, and transparent, further enhancing the reliability of the data graph construction process.

## Metadata-Driven Conversations: A Dynamic Workflow

The agent's ability to hold a dynamic, intelligent conversation is a core pattern of this architecture, moving beyond the rigidity of traditional systems. This workflow is driven entirely by metadata, not by a hardcoded script.

### The Old Way: The Static Template

Traditional systems, like assessment platforms, rely on static templates. A product manager and engineer must pre-define a rigid script of questions. If a new business requirement emerges (e.g., needing to track a new attribute for all vendors), the template itself must be manually updated and redeployed. This process is slow, brittle, and doesn't adapt to information that might already be present in a source document.

### The New Way: The Dynamic Dialogue

This agent-driven approach is fully dynamic, transforming a fixed questionnaire into an intelligent interview. The agent follows a simple but powerful three-step process for every entity it encounters:

1.  **Discover**: The agent identifies a potential new entity in the source document, for example, a vendor named 'PaySecure'.
2.  **Consult**: It immediately calls the **`get_entity_parameters(entity_type='Vendor')`** tool. The tool returns the "rules" for a Vendor from the central metadata repository—for instance, that `contact_email` is a **required** attribute and `dpa_signed` is an *optional* one.
3.  **Reconcile & Inquire**: The agent first checks if the policy text already contains the required information. If not, it intelligently formulates a question to the user to capture the missing mandatory data. It may then ask about optional fields if appropriate.

### The "Future-Proof" Advantage

This makes the system incredibly flexible and "future-proof." If an administrator adds a new mandatory attribute like `privacy_contact_dl` to the 'Vendor' entity in the database, the agent will **automatically** start asking for that information during its next analysis—without any changes to the agent's code or prompts. The conversation logic is completely decoupled from the agent's core programming.

This is the difference between a call center agent who can only read from a fixed script and an experienced detective who knows what questions to ask based on the clues they uncover. The agent doesn't follow a script; it follows the data.

---

## A Practical Example: Processing a Privacy Policy (Expanded)

Here is a more detailed walkthrough of the single-agent workflow processing the sample policy, now covering a wider range of entities and their relationships.

### The Source Document: Comprehensive Privacy Policy
> **...**
> ## 1. Introduction
> ...Our main data processing activities include providing our **SaaS Platform**, **marketing**, and **customer support**. Our primary data storage is the **Production AWS RDS**... User authentication is a key processing activity that uses this database.
> ## 2. Data We Collect
> - **Contact Information**: We collect **user names** and **email addresses** during account setup. This data belongs to our **Customers**.
> - **Technical Information**: ...sent to **AnalyticsCorp** for product improvement.
> ## 5. Data Subject Rights
> Users, who are primarily **EU Customers** and **US-based Employees**, have the right to access...
> **...**

### Step 1 & 2: Gaining Context and Parsing
The **Agent** begins its process. It first calls the metadata tools (`get_entity_types`, `get_relationship_ontology`) to learn the schema. It then parses the document, identifying a rich set of potential entities:
* **Assets**: `Production AWS RDS`
* **Vendors**: `AnalyticsCorp`
* **Processing Activities**: `SaaS Platform`, `Marketing`, `Customer Support`, `User Authentication`
* **Data Elements**: `user names`, `email addresses`
* **Data Subject Types**: `Customers`, `EU Customers`, `US-based Employees`

### Step 3: Disambiguation with Tools
The agent uses **`find_similar_entities()`** for each term to reconcile them against the system's knowledge:
* It finds no existing asset named `Production AWS RDS` and flags it as **new**.
* It finds a strong match for `user names` with the pre-seeded **"Full Name"** Data Element.
* It finds strong matches for both `Customers` and `EU Customers` with the pre-seeded **"Customer"** Data Subject Type.
* It finds a strong match for `US-based Employees` with the pre-seeded **"Employee"** Data Subject Type.

### Step 4: Dynamic Data Collection, Confirmation, and Construction
The agent presents its comprehensive findings and uses metadata to begin the dynamic conversation, moving seamlessly from analysis to construction within the same session.

> **AGENT:** "I have analyzed the policy and have the following proposals:
>
> **New Entities Identified:**
> * **Asset**: `Production AWS RDS`
> * **Vendor**: `AnalyticsCorp`
> * **Processing Activities**: `SaaS Platform`, `Marketing`, `Customer Support`, `User Authentication`
>
> **System Matches:**
> * The policy mentions `user names`, which I've matched to the system's **'Full Name'** Data Element.
> * It mentions `Customers` and `EU Customers`, which I've matched to the **'Customer'** Data Subject Type.
> * It mentions `US-based Employees`, which I've matched to the **'Employee'** Data Subject Type.
>
> Now, before I create the new **Asset** `Production AWS RDS`, the system requires a mandatory 'hosting\_location'. Could you please provide that?"
>
> **USER:** "us-west-2"
>
> **AGENT:** "Thank you. Based on the policy and the system's rules, I've also inferred this web of relationships:
> * `ProcessingActivity('User Authentication')` **USES** `Asset('Production AWS RDS')`
> * `Asset('Production AWS RDS')` **CONTAINS** `DataElement('Full Name')`
> * `Asset('Production AWS RDS')` **CONTAINS** data about `DataSubjectType('Customer')`
> * `ProcessingActivity('Marketing')` is **ASSISTED_BY** `Vendor('AnalyticsCorp')`
>
> Do you approve this full plan? Once approved, I will commit these changes to the data graph."

### Step 5: Final Validation and Creation
The user approves. The agent, having all the confirmed and enriched data within its active context, proceeds with the final, validated creation of all new entities and their complex relationships in the database. The entire process is a single, auditable transaction.

---

## Conclusion: Reliability Through a Unified Session

This detailed example demonstrates the power of the blueprint. The system successfully navigated a real-world policy by:
1.  **Using a Single-Agent Architecture** to maintain a context-rich session, preventing the information loss common in unreliable multi-agent relay systems.
2.  **Externalizing its "Brain"** into the MCP toolbox, which relies on the company's own seeded data and rules as the ultimate source of truth.
3.  **Driving Conversations Dynamically** with metadata, ensuring all required information is captured in a flexible and future-proof way within a continuous dialogue.

This architecture creates a reliable, transparent, and auditable system that keeps the human expert in control. By prioritizing a seamless, stateful user session, it sets the standard for building enterprise-grade AI applications for complex domains.