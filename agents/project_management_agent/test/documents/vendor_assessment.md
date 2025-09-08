# Vendor Security & Privacy Assessment

## Vendor Information

**Vendor Name**: Segment CDP (Twilio Segment)  
**Vendor ID**: VEN-SEGMENT-01  
**Assessment Date**: September 15, 2025  
**Assessment Conducted By**: Alex Rodriguez, Privacy Officer  
**Assessment Status**: Completed  

## Vendor Overview

Segment is a Customer Data Platform (CDP) that helps organizations collect, clean, and control customer data. The platform enables businesses to collect user events from web and mobile apps, provide a complete data collection API, and send data to analytics tools and marketing platforms.

**Primary Services Used**:
- Data Collection & Integration
- Identity Resolution
- Audience Management
- Data Governance

**Website**: https://segment.com  
**Headquarters**: San Francisco, CA, USA  

## Data Processing Details

### Data Categories Processed

| Data Category | Description | Sensitivity |
|---------------|-------------|------------|
| Personal Information | Names, email addresses, phone numbers | High |
| Device Information | IP addresses, device IDs, cookies | Medium |
| Behavioral Data | Website interactions, app usage, purchase history | Medium |
| Location Data | Country, city, GPS coordinates (if enabled) | High |
| Transaction Data | Purchase amounts, products, payment methods (no full payment details) | High |

### Processing Locations

- **Primary Processing**: United States (Oregon, Virginia)
- **Secondary Processing**: European Union (Ireland)
- **Data Storage**: United States, European Union
- **Support Operations**: United States, India

### Sub-processors

1. **Amazon Web Services (AWS)**
   - Role: Cloud infrastructure provider
   - Location: Global (multiple regions)
   
2. **Google Cloud Platform**
   - Role: Data analytics and machine learning
   - Location: Global (multiple regions)
   
3. **Snowflake**
   - Role: Data warehousing
   - Location: United States, EU

## Security Controls Assessment

| Control Area | Status | Notes |
|--------------|--------|-------|
| Access Control | ✅ Satisfactory | Role-based access with MFA; privileged access management |
| Encryption | ✅ Satisfactory | Data encrypted in transit (TLS 1.3) and at rest (AES-256) |
| Network Security | ✅ Satisfactory | Firewalls, IDS/IPS, regular penetration testing |
| Vulnerability Management | ✅ Satisfactory | Monthly scanning, timely patching, bug bounty program |
| Incident Response | ✅ Satisfactory | Documented procedures, 24/7 SOC, 4-hour notification SLA |
| Business Continuity | ⚠️ Needs Improvement | RPO/RTO meets requirements but failover testing infrequent |
| Physical Security | ✅ Satisfactory | Relies on AWS/GCP physical security controls |
| Employee Security | ✅ Satisfactory | Background checks, security training, access reviews |

## Privacy Controls Assessment

| Control Area | Status | Notes |
|--------------|--------|-------|
| Privacy Policy | ✅ Satisfactory | Comprehensive, clear, last updated June 2025 |
| Data Subject Rights | ✅ Satisfactory | Automated processes for access, deletion, portability |
| Consent Management | ⚠️ Needs Improvement | Limited granular consent options for end-users |
| Data Minimization | ✅ Satisfactory | Configurable data collection and retention |
| Purpose Limitation | ✅ Satisfactory | Clear documentation of processing purposes |
| Cross-border Transfers | ✅ Satisfactory | SCCs in place, supplementary measures documented |
| Data Protection Impact Assessment | ✅ Satisfactory | Conducted for high-risk processing |
| Data Breach Notification | ✅ Satisfactory | 24-hour notification commitment |

## Compliance Certifications

- ISO 27001:2022 (Information Security Management)
- SOC 2 Type II (Security, Availability, Confidentiality)
- HIPAA Compliance (for healthcare customers)
- GDPR Compliance Program
- CCPA/CPRA Compliance Program

## Risk Assessment

| Risk | Likelihood | Impact | Risk Level | Mitigation |
|------|------------|--------|------------|------------|
| Data Breach | Low | High | Medium | Encryption, access controls, security monitoring |
| Unauthorized Access | Low | High | Medium | MFA, role-based access, access reviews |
| Regulatory Non-compliance | Low | High | Medium | Compliance program, regular assessments |
| Service Disruption | Medium | Medium | Medium | SLAs, redundancy, failover capabilities |
| Sub-processor Issues | Medium | Medium | Medium | Sub-processor monitoring, contractual safeguards |

## Contractual Safeguards

- Data Processing Agreement (DPA) signed on August 30, 2025
- Standard Contractual Clauses (SCCs) implemented
- Liability provisions and insurance requirements met
- Security and privacy requirements included in MSA
- Breach notification requirements: 24 hours
- Right to audit clause included and accepted

## Recommendations

1. **Approve with Conditions**:
   - Require implementation of more granular consent management options
   - Request quarterly business continuity testing reports
   - Implement additional monitoring for data access patterns

2. **Risk Mitigation Actions**:
   - Document data flows with this vendor in the data inventory
   - Configure data retention periods to minimum necessary
   - Implement regular access reviews for vendor accounts
   - Conduct annual reassessment of security and privacy controls

## Approval

**Decision**: Approved with Conditions  
**Approver**: Maria Chen, Chief Privacy Officer  
**Approval Date**: September 20, 2025  
**Next Review Date**: September 20, 2026  

**Conditions for Approval**:
1. Vendor must address consent management limitations within 90 days
2. Quarterly business continuity testing reports must be provided
3. Annual reassessment required before renewal
