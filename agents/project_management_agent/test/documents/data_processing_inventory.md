# Data Processing Activities Inventory

## Overview

This document provides a comprehensive inventory of data processing activities related to the Customer Data Platform (CDP) Integration Project. The inventory is maintained as part of our privacy governance program and serves as a record of processing activities as required by various privacy regulations.

**Last Updated**: September 25, 2025  
**Maintained By**: Privacy Governance Team  
**Review Frequency**: Quarterly  

## Processing Activities

### 1. Customer Data Collection

**Activity ID**: PROC-CDP-COLLECT-01  
**Description**: Collection of customer data from various sources including website, mobile apps, CRM, and third-party services  
**Business Purpose**: To create a unified view of customer interactions and enable personalized marketing  
**Process Owner**: Marketing Operations Team  

#### Data Elements

| Data Element | Category | Special Category | Source System |
|--------------|----------|------------------|--------------|
| Full Name | Personal Data | No | CRM-SALESFORCE-01 |
| Email Address | Personal Data | No | CRM-SALESFORCE-01, MAP-HUBSPOT-01 |
| Phone Number | Personal Data | No | CRM-SALESFORCE-01 |
| Mailing Address | Personal Data | No | CRM-SALESFORCE-01, ECOM-SHOPIFY-01 |
| Date of Birth | Personal Data | No | CRM-SALESFORCE-01 |
| Purchase History | Customer Data | No | ECOM-SHOPIFY-01 |
| Browsing Behavior | Behavioral Data | No | Website Analytics |
| Device Information | Technical Data | No | Website Analytics, Mobile App |
| IP Address | Technical Data | No | Website Analytics, Mobile App |
| Location Data | Location Data | No | Mobile App (if permitted) |

#### Processing Details

**Legal Basis**: 
- Consent (for marketing communications)
- Legitimate Interest (for analytics and service improvement)
- Contract Fulfillment (for purchases and account management)

**Data Subjects**: Customers, Prospects, Website Visitors

**Data Retention**: 
- Active customers: Duration of relationship + 3 years
- Prospects: 2 years from last interaction
- Website visitors: 13 months

**Cross-Border Transfers**: Yes (US to EU, EU to US)
- Transfer Mechanism: Standard Contractual Clauses

**Security Measures**:
- Encryption in transit and at rest
- Access controls based on role
- Regular security assessments

### 2. Customer Profile Unification

**Activity ID**: PROC-CDP-UNIFY-01  
**Description**: Matching and merging customer identifiers across channels to create unified customer profiles  
**Business Purpose**: To eliminate data silos and create a single customer view  
**Process Owner**: Data Science Team  

#### Data Elements

| Data Element | Category | Special Category | Source System |
|--------------|----------|------------------|--------------|
| Customer ID | Identifier | No | CRM-SALESFORCE-01 |
| Email Address | Personal Data | No | Multiple Systems |
| Phone Number | Personal Data | No | Multiple Systems |
| Device ID | Technical Data | No | Website, Mobile App |
| Cookie ID | Technical Data | No | Website |
| Social Media ID | Identifier | No | Social Media Integrations |

#### Processing Details

**Legal Basis**: 
- Legitimate Interest (for creating unified customer view)
- Consent (for specific marketing uses of unified profiles)

**Data Subjects**: Customers, Prospects

**Data Retention**: 
- 2 years after last customer interaction

**Cross-Border Transfers**: Yes (US to EU, EU to US)
- Transfer Mechanism: Standard Contractual Clauses

**Security Measures**:
- Pseudonymization where possible
- Encryption of identifiers
- Strict access controls

### 3. Audience Segmentation

**Activity ID**: PROC-CDP-SEGMENT-01  
**Description**: Grouping customers based on attributes, behaviors, and preferences  
**Business Purpose**: To enable targeted marketing campaigns and personalized experiences  
**Process Owner**: Marketing Analytics Team  

#### Data Elements

| Data Element | Category | Special Category | Source System |
|--------------|----------|------------------|--------------|
| Demographic Information | Personal Data | No | Unified Customer Profile |
| Purchase History | Customer Data | No | Unified Customer Profile |
| Website Behavior | Behavioral Data | No | Unified Customer Profile |
| Product Preferences | Preference Data | No | Derived Data |
| Engagement Scores | Derived Data | No | Derived Data |
| Propensity Models | Derived Data | No | Derived Data |

#### Processing Details

**Legal Basis**: 
- Legitimate Interest (for standard segmentation)
- Consent (for advanced personalization)

**Data Subjects**: Customers, Prospects

**Data Retention**: 
- Segments updated continuously
- Historical segments retained for 1 year

**Cross-Border Transfers**: Yes (US to EU, EU to US)
- Transfer Mechanism: Standard Contractual Clauses

**Security Measures**:
- Aggregation where possible
- Access limited to marketing team
- Regular audit of segment criteria

### 4. Campaign Activation

**Activity ID**: PROC-CDP-ACTIVATE-01  
**Description**: Using customer segments to deliver targeted marketing campaigns across channels  
**Business Purpose**: To improve marketing effectiveness and customer engagement  
**Process Owner**: Campaign Management Team  

#### Data Elements

| Data Element | Category | Special Category | Source System |
|--------------|----------|------------------|--------------|
| Email Address | Personal Data | No | Unified Customer Profile |
| Phone Number | Personal Data | No | Unified Customer Profile |
| Device ID | Technical Data | No | Unified Customer Profile |
| Segment Membership | Derived Data | No | Audience Segmentation |
| Channel Preferences | Preference Data | No | Unified Customer Profile |
| Opt-out Status | Preference Data | No | Consent Management System |

#### Processing Details

**Legal Basis**: 
- Consent (for direct marketing communications)
- Legitimate Interest (for existing customer communications)

**Data Subjects**: Customers, Prospects (with consent)

**Data Retention**: 
- Campaign data retained for 6 months after campaign completion
- Performance metrics retained for 2 years

**Cross-Border Transfers**: Yes (US to EU, EU to US)
- Transfer Mechanism: Standard Contractual Clauses

**Security Measures**:
- Encryption of transmission data
- Pre-campaign privacy reviews
- Automated suppression of opt-outs

### 5. Analytics and Reporting

**Activity ID**: PROC-CDP-ANALYTICS-01  
**Description**: Analysis of customer data and campaign performance to generate insights  
**Business Purpose**: To measure effectiveness and inform business decisions  
**Process Owner**: Business Intelligence Team  

#### Data Elements

| Data Element | Category | Special Category | Source System |
|--------------|----------|------------------|--------------|
| Aggregated Customer Data | Aggregated Data | No | Data Warehouse |
| Campaign Performance | Business Data | No | Marketing Platforms |
| Conversion Metrics | Business Data | No | Website, E-commerce |
| Customer Lifetime Value | Derived Data | No | Calculated |
| Attribution Data | Business Data | No | Marketing Platforms |

#### Processing Details

**Legal Basis**: 
- Legitimate Interest (for business analytics)

**Data Subjects**: Customers (aggregated)

**Data Retention**: 
- Detailed reports: 2 years
- Aggregated statistics: 5 years

**Cross-Border Transfers**: Yes (US to EU, EU to US)
- Transfer Mechanism: Standard Contractual Clauses

**Security Measures**:
- Aggregation and anonymization where possible
- Role-based access to reports
- Data minimization in reporting

## Data Processors

### Primary Processors

1. **Segment CDP**
   - **Processor ID**: VEN-SEGMENT-01
   - **Role**: Customer Data Platform provider
   - **Processing Activities**: PROC-CDP-COLLECT-01, PROC-CDP-UNIFY-01, PROC-CDP-SEGMENT-01
   - **Location**: United States
   - **DPA Status**: Signed (August 30, 2025)
   - **Transfer Mechanism**: SCCs with supplementary measures

2. **Snowflake**
   - **Processor ID**: VEN-SNOWFLAKE-01
   - **Role**: Data warehouse provider
   - **Processing Activities**: PROC-CDP-ANALYTICS-01
   - **Location**: United States, EU
   - **DPA Status**: Signed (July 15, 2025)
   - **Transfer Mechanism**: SCCs with supplementary measures

3. **Fivetran**
   - **Processor ID**: VEN-FIVETRAN-01
   - **Role**: ETL provider
   - **Processing Activities**: PROC-CDP-COLLECT-01
   - **Location**: United States
   - **DPA Status**: In Progress
   - **Transfer Mechanism**: SCCs pending

### Sub-processors

1. **Amazon Web Services**
   - **Processor ID**: SUB-AWS-01
   - **Role**: Cloud infrastructure provider
   - **Processing Activities**: All
   - **Location**: Global
   - **Oversight**: Through primary processor agreements

2. **Google Cloud Platform**
   - **Processor ID**: SUB-GCP-01
   - **Role**: Analytics infrastructure
   - **Processing Activities**: PROC-CDP-ANALYTICS-01
   - **Location**: Global
   - **Oversight**: Through primary processor agreements

## Privacy Controls

### Data Subject Rights Management

**Process Owner**: Privacy Office
**Tools Used**: OneTrust DSR Manager
**SLA**: 15 calendar days

| Right | Implementation | Responsible Party |
|-------|----------------|------------------|
| Access | Automated data export from CDP | Privacy Office, IT |
| Rectification | Manual updates to source systems | Data Stewards |
| Erasure | Automated deletion workflow | Privacy Office, IT |
| Restriction | Manual flagging in systems | Data Stewards |
| Portability | Automated data export in machine-readable format | IT |
| Objection | Preference center + manual processing | Marketing, Privacy Office |

### Consent Management

**Process Owner**: Marketing Operations
**Tools Used**: OneTrust Consent Management Platform
**Consent Types Tracked**:
- Marketing communications (email, SMS, phone)
- Cookies and tracking technologies
- Personalization and profiling
- Third-party data sharing

### Data Protection Impact Assessment

**DPIA Conducted**: Yes
**Date**: August 15, 2025
**Outcome**: Approved with mitigations
**Key Risks Identified**:
1. Extensive data combination creating high-risk profiles
2. Cross-border data transfers
3. Automated decision-making for marketing

**Mitigations Implemented**:
1. Enhanced consent mechanisms
2. Data minimization controls
3. Human oversight of automated decisions
4. Additional security measures

## Compliance Documentation

- Data Protection Impact Assessment (August 15, 2025)
- Legitimate Interest Assessment (August 10, 2025)
- Vendor Security Assessments (Various dates)
- Data Processing Agreements (Various dates)
- Records of Consent (Ongoing)
- Data Flow Diagrams (September 1, 2025)
- Security Controls Documentation (September 5, 2025)
