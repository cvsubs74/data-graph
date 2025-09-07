# Vendor Risk Analysis System Architecture

## Introduction

This document outlines the implementation of the vendor risk analysis system. The architecture uses a simplified agent-as-tool pattern with an orchestrator agent that guides the user through the risk assessment process while leveraging specialized tools and sub-agents for specific tasks.

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
│  │ Web Scraper Tool    │  │ MCP Toolset     │  │ Researcher Agent  │   │
│  │ (URL Validation)    │  │ (Risk Questions)│  │ (As Tool)         │   │
│  │                     │  │                 │  │                   │   │
│  └─────────────────────┘  └─────────────────┘  └───────────────────┘   │
│                                                                         │
├─────────────────────────────────────────────────────────────────────────┤
│                           BACKEND SERVICES                              │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  ┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐   │
│  │                 │     │                 │     │                 │   │
│  │  Web Scraper    │     │  Google Search  │     │ Risk Questions  │   │
│  │     Tool        │     │      Tool       │     │     Service     │   │
│  │                 │     │                 │     │                 │   │
│  └─────────────────┘     └─────────────────┘     └─────────────────┘   │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

## Current Implementation Workflow

The implementation uses a simplified architecture with a main orchestrator agent that guides the user through the entire risk assessment process. This agent leverages specialized tools and a researcher sub-agent to perform specific tasks.

### 1. Autonomous Vendor Risk Agent (Main Orchestrator)

**Purpose**: Guide the user through the complete vendor risk assessment process from start to finish.

**Responsibilities**:
- Introduce itself and explain capabilities upon launch
- Guide the user through a structured workflow with explicit confirmation at each step
- Coordinate the use of specialized tools for different assessment phases
- Synthesize information into a comprehensive final report
- Ensure proper source citations throughout the process

**Workflow Sequence**:
1. **URL Validation**: Use web scraper tool to analyze vendor website
2. **Risk Question Generation**: Use MCP toolset to retrieve standardized risk questions
3. **Research**: Leverage researcher agent to find answers to risk questions
4. **Report Generation**: Automatically compile findings into a comprehensive report
5. **Final Confirmation**: Ask for user feedback on the report

**Tools Used**:
- Web scraper tool for URL validation
- MCP toolset for risk questions
- Researcher agent (as a tool) for in-depth research

### 2. Vendor Researcher Agent (Specialist Sub-Agent)

**Purpose**: Conduct targeted research to answer specific risk assessment questions about vendors.

**Responsibilities**:
- Use Google search to find relevant information about vendors
- Focus on security, privacy, compliance, and reliability information
- Provide detailed, factual answers with proper source citations
- Format answers with clear question-answer-source structure
- Verify that all URLs are complete and come directly from search results

**Input**:
- Vendor name/URL and specific risk assessment questions

**Output**:
- Detailed research findings with answers to risk questions
- Each answer includes specific source citations
- All URLs are properly formatted and verified

**Tools Used**:
- Google search tool

## Backend Services

The system relies on several backend services and tools to perform its functions:

### 1. Web Scraper Tool

**Purpose**: Extract and analyze content from vendor websites.

**Functionality**:
- Scrapes website content from provided URLs
- Extracts key information about the vendor
- Validates that the URL is legitimate and operational

### 2. MCP Toolset

**Purpose**: Provide access to standardized risk assessment questions and other MCP services.

**Functionality**:
- Retrieves standardized risk questions based on vendor type
- Organizes questions by risk category
- Provides question metadata (type, importance, etc.)

### 3. Google Search Tool

**Purpose**: Enable comprehensive research on vendors.

**Functionality**:
- Performs web searches for vendor information
- Returns relevant search results with complete URLs
- Supports targeted queries for specific risk areas

## Implementation Considerations

### User Interaction and Confirmation

The system is designed with explicit user confirmation at key decision points:

1. **After URL Validation**: The user must confirm before proceeding to risk questions
2. **After Question Generation**: The user can review, add, remove, or modify questions
3. **After Report Generation**: The user can request revisions to the final report

### Source Citation Requirements

The system enforces strict source citation standards:

- Every claim and answer must include specific source citations
- Citations must use real, complete URLs from search results
- URLs must be properly formatted without extra characters
- A comprehensive references section is included in the final report

### Automatic Report Generation

The system automatically generates a comprehensive report after research is completed:

- Executive Summary
- Vendor Profile
- Risk Assessment Methodology
- Risk Assessment Results
- FAQ section with verified answers to risk questions
- Recommendations with source citations
- Verification Statement
- References section

## Conclusion

The current vendor risk analysis system uses a simplified but effective architecture with a main orchestrator agent and specialized tools. This approach provides a streamlined user experience while maintaining the thoroughness and reliability needed for vendor risk assessment. The system's emphasis on explicit user confirmation, proper source citations, and comprehensive reporting ensures that the final risk assessment is both accurate and useful for business decision-making.
