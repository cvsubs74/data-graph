# Domain-Driven Agentic Blueprint: Data Graph Construction for Privacy Governance

## Introduction: Architecture as a Consequence, Not a Goal

This document outlines a blueprint for a multi-agent system designed specifically for the complex domain of **privacy policy analysis and data graph construction**. It's crucial to understand that the agentic architecture presented here is not an abstract framework; it is a direct consequence of the problem's unique challenges. The primary goal is not simply to "build agents," but to create a transparent, verifiable, and user-centric system for navigating the nuanced and high-stakes world of data privacy.

The core principle is **domain-first design**. The architecture serves the task, not the other way around. To illustrate why this specific multi-agent approach was chosen, we will contrast it with a simpler, monolithic agent approach, demonstrating how the separation of concerns is essential for achieving trustworthiness and accuracy in this domain.

---

## Architectural Philosophy: The Case for Specialization

In a domain as sensitive as privacy compliance, a single "black box" agent that ingests a policy and outputs a finished graph is brittle and untrustworthy. It provides no opportunity for expert human oversight and is incredibly difficult to debug when it misinterprets ambiguous legal language.

Therefore, our philosophy is rooted in creating a system of **specialized, collaborating agents**, where each agent has a single, well-defined responsibility. This approach transforms an opaque process into a transparent, step-by-step workflow that empowers the user. It's the difference between hiring a single generalist to build a house from foundation to finish and hiring a specialized architect, a construction crew, and an inspector—each an expert in their part of the process.

---

## Architectural Fork in the Road: Monolithic vs. Multi-Agent Approach

To solve the problem of converting a privacy policy into a structured data graph, one could take two distinct paths.

#### Path A: The Monolithic Agent Approach (The "Black Box")
A single, powerful agent would be tasked with the entire end-to-end process:
1.  Read the entire privacy policy.
2.  Internally parse the text, identify all potential entities (like vendors, data types, and processing activities), and infer their relationships.
3.  Simultaneously search for existing entities in the database to avoid duplicates.
4.  Construct the entire graph representation in one large, complex operation.
5.  Present the final, completed graph to the user for approval.

While conceptually simpler, this approach suffers from critical flaws in this domain:
* **Lack of Transparency:** If an error occurs (e.g., a vendor is misidentified), it's nearly impossible to pinpoint where in the agent's complex reasoning the mistake was made.
* **Difficult Correction:** The user is presented with a "take it or leave it" final product. Correcting a single error might require rejecting the entire graph and starting over.
* **Cognitive Overload:** The agent juggles multiple contexts simultaneously—linguistic analysis, semantic similarity, and graph theory—making its logic brittle and hard to maintain.

#### Path B: The Multi-Agent System (The "Assembly Line") - **This Blueprint's Choice**
This approach, detailed below, breaks the problem down into a logical sequence of specialized tasks performed by distinct agents. It prioritizes clarity, verifiability, and human-in-the-loop validation.

---

## Core Architectural Patterns of the Multi-Agent System

This system is built on several key patterns that directly address the shortcomings of the monolithic approach.

#### 1. Specialized Agent Roles: The Linguist and The Logician 🧠
The architecture employs a sharp separation of concerns, creating two primary agents with distinct expertise.

* **Document Analysis Agent (The Linguist)**: This agent's sole focus is on understanding unstructured text.
    * **Responsibilities**: It scrapes the raw text from privacy policies, performs entity extraction (e.g., identifying "Google Analytics" as a 'Vendor'), and classifies these findings based on descriptions in the system's metadata.
    * **Domain-Specific Function**: Crucially, it presents its findings in **plain business language**, hiding technical details like similarity scores. It acts as a translator, converting messy legal prose into a structured list of candidates. For example, it will say, "I found a potential new vendor named 'Stripe.' Does this seem correct?"
    * **Key Behavior**: It does not act further. It **waits for user confirmation** before passing its structured, validated output to the next stage.

* **Graph Construction Agent (The Logician)**: This agent is an expert in rules, logic, and structure. It knows nothing about parsing documents.
    * **Responsibilities**: It receives the user-validated, structured data from the Analysis Agent. Its job is to integrate this data into the formal data graph one piece at a time.
    * **Domain-Specific Function**: It rigorously enforces the system's rules by validating every proposed relationship against the predefined **ontology**. For example, it will check if the relationship `Data Element 'Email Address' -> IS_PROCESSED_BY -> Processing Activity 'Marketing'` is a valid connection according to the rules.
    * **Key Behavior**: It processes entities **incrementally**, asking for user confirmation at each step ("Shall I add 'Stripe' as a Vendor and connect it to the 'Payment Processing' activity?"). This ensures the graph is built correctly, piece by piece.

#### 2. Sequential Orchestration Pattern: A Deliberate, Linear Workflow
The process is intentionally linear and controlled, managed by a `SequentialAgent` orchestrator.
* **Fixed Execution Order**: The Linguist *must* run before the Logician. You cannot structure data you haven't yet analyzed. This mirrors a logical human workflow.
* **State Passing**: The output from the Document Analysis Agent (the user-confirmed list of entities) is saved to a shared session state. The Graph Construction Agent then reads from this state, ensuring a clean and explicit handoff of information.
* **Single Entry Point**: The user interacts with a single "root" agent, which orchestrates this sequential flow, simplifying the user experience.

#### 3. Metadata-Driven Governance: The System's "Rulebook" 📖
The MCP (Master Control Program) server and its tools are not just a database; they are the source of truth and the rulebook for the entire privacy domain.
* **The Ontology as Law**: The metadata tables (`EntityTypes`, `RelationshipOntology`) define the reality of the system. They dictate what types of entities can exist and how they are allowed to interact. The agents don't guess; they consult this rulebook.
* **Tools as Enforcement**: The CRUD and semantic search tools provided by the server are the agents' only way to interact with the data. These tools have built-in validation that enforces the ontology, preventing the Graph Construction Agent from ever creating an invalid relationship.
* **Transactional Integrity**: All database operations are wrapped in transactions. If any part of a multi-step graph update fails, the entire operation is rolled back, preventing the graph from entering a corrupt or inconsistent state.

#### 4. Human-in-the-Loop (HITL) Validation: The Trust Layer 🙏
This is arguably the most critical pattern for a governance tool. The system is designed to augment, not replace, human expertise.
* **Staged Confirmation**: The system never takes a major action without explicit permission. First, the Analysis Agent asks for confirmation on its *findings*. Then, the Construction Agent asks for confirmation on its proposed *actions*.
* **Business-Friendly Abstraction**: The user is never shown a similarity score like `0.92`. Instead, the system presents a clear choice: "I found something called 'Google Marketing Platform.' This is very similar to the existing vendor 'Google Analytics.' Are they the same thing, or is this a new vendor?"
* **Incremental Build**: By processing entities one by one with confirmation, the user can easily track progress and catch errors early, building confidence and trust in the final output.

#### 5. Vector Embedding Similarity Search: Disambiguation and Intelligence 🔍
This pattern addresses the challenge of varied terminology in privacy policies.
* **Semantic Understanding**: Using a model like Gemini, the system converts entity names and descriptions into vector embeddings. This allows it to understand that "payment processor" and "credit card handler" are semantically similar concepts, even if the keywords don't match exactly.
* **De-duplication Guardrail**: Its primary role in this architecture is to prevent the creation of duplicate entities. Before suggesting a new vendor, the Analysis Agent performs a similarity search to see if a similar one already exists, flagging it for the user as described above.
* **Strict System Boundaries**: The semantic search operates only on the data already within the system. It doesn't search the open web, preventing the introduction of irrelevant or incorrect information.

---

### Technical Implementation & Key Strengths

The implementation details (Spanner, Cloud Run, Vertex AI) support this domain-driven architecture. The key strengths arise directly from the choice of the multi-agent, human-in-the-loop model over a monolithic one.

1.  **Trustworthy & Auditable Operation**: The step-by-step, user-confirmed workflow creates a clear audit trail and ensures the human expert is the final arbiter of truth.
2.  **Transparent & Modular Execution**: By separating the "Linguist" and the "Logician," the system is easier to debug, maintain, and upgrade. You can swap out the embedding model without affecting the graph validation logic.
3.  **Domain-Centric Validation**: The metadata-driven approach ensures the final data graph is always consistent with the established rules of the privacy domain.
4.  **Semantic Intelligence**: The use of vector embeddings provides a powerful yet controlled mechanism for handling the inherent ambiguity of natural language in legal documents.

---

### Future Enhancement Opportunities

The modular nature of this architecture allows for straightforward enhancements:

1.  **Parallel Agent Processing**: While the core workflow is sequential, multiple `Document Analysis Agents` could be run in parallel on different documents, with their outputs queued for a single `Graph Construction Agent`.
2.  **Feedback Loop Integration**: The system could learn from user corrections. When a user merges two entities the system thought were different, that information can be used to fine-tune future similarity suggestions.
3.  **Enhanced Visualization**: An additional `Visualization Agent` could be added to the sequence to generate and display interactive graph diagrams for the user at various stages.