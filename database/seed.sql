-- =================================================================
-- ===== 3. SEED ONTOLOGY METADATA (DML)                       =====
-- =================================================================
-- This section populates the fresh schema with foundational data.
-- It uses UPSERT to be idempotent.

-- 3.1. Seed the EntityTypes table
UPSERT INTO EntityTypes (type_id, name, description, table_name, id_column, created_at, updated_at) VALUES
  ('2b6291d5-f623-4a12-8b3a-59d04f145459', 'Asset', 'A system, application, or database.', 'Assets', 'asset_id', PENDING_COMMIT_TIMESTAMP(), PENDING_COMMIT_TIMESTAMP()),
  ('8b5f3a0a-9c9a-41f2-8c9a-4a6f9f3c1d0b', 'ProcessingActivity', 'A business process that uses data.', 'ProcessingActivities', 'activity_id', PENDING_COMMIT_TIMESTAMP(), PENDING_COMMIT_TIMESTAMP()),
  ('f3a2c5b1-9b1a-4e2b-8d1a-6f3b1a4e2b8d', 'DataElement', 'A specific category of personal data.', 'DataElements', 'element_id', PENDING_COMMIT_TIMESTAMP(), PENDING_COMMIT_TIMESTAMP()),
  ('c5b1a4e2-8d1a-4e2b-9b1a-3b1a4e2b8d1a', 'DataSubjectType', 'A category of individual.', 'DataSubjectTypes', 'subject_id', PENDING_COMMIT_TIMESTAMP(), PENDING_COMMIT_TIMESTAMP()),
  ('a4e2b8d1-6f3b-4e2b-8d1a-9b1a4e2b8d1a', 'Vendor', 'A third-party company or service.', 'Vendors', 'vendor_id', PENDING_COMMIT_TIMESTAMP(), PENDING_COMMIT_TIMESTAMP());

-- 3.2. Seed the EntityTypeProperties table
UPSERT INTO EntityTypeProperties (type_id, property_name, data_type, is_required, description, created_at, updated_at) VALUES
  ('2b6291d5-f623-4a12-8b3a-59d04f145459', 'hosting_location', 'STRING', TRUE, 'The physical or cloud region where the asset is hosted.', PENDING_COMMIT_TIMESTAMP(), PENDING_COMMIT_TIMESTAMP()),
  ('2b6291d5-f623-4a12-8b3a-59d04f145459', 'data_retention_days', 'INTEGER', FALSE, 'Number of days data is retained in this asset.', PENDING_COMMIT_TIMESTAMP(), PENDING_COMMIT_TIMESTAMP()),
  ('a4e2b8d1-6f3b-4e2b-8d1a-9b1a4e2b8d1a', 'contact_email', 'STRING', TRUE, 'The primary contact email for the vendor.', PENDING_COMMIT_TIMESTAMP(), PENDING_COMMIT_TIMESTAMP()),
  ('a4e2b8d1-6f3b-4e2b-8d1a-9b1a4e2b8d1a', 'dpa_signed', 'BOOLEAN', FALSE, 'Indicates if a Data Processing Agreement is signed.', PENDING_COMMIT_TIMESTAMP(), PENDING_COMMIT_TIMESTAMP()),
  ('f3a2c5b1-9b1a-4e2b-8d1a-6f3b1a4e2b8d', 'sensitivity_level', 'STRING', TRUE, 'The sensitivity level of the data (e.g., Public, Confidential, Secret).', PENDING_COMMIT_TIMESTAMP(), PENDING_COMMIT_TIMESTAMP());

-- 3.3. Seed the DataElements table
UPSERT INTO DataElements (element_id, name, description, created_at, updated_at) VALUES
  ('e1a2b3c4-d5e6-4f7g-8h9i-0j1k2l3m4n5o', 'Email Address', 'User email address used for account identification and communication.', PENDING_COMMIT_TIMESTAMP(), PENDING_COMMIT_TIMESTAMP()),
  ('f2b3c4d5-e6f7-5g8h-9i0j-1k2l3m4n5o6p', 'Full Name', 'User full name including first and last name.', PENDING_COMMIT_TIMESTAMP(), PENDING_COMMIT_TIMESTAMP()),
  ('g3c4d5e6-f7g8-6h9i-0j1k-2l3m4n5o6p7q', 'Phone Number', 'User phone number for account verification and communication.', PENDING_COMMIT_TIMESTAMP(), PENDING_COMMIT_TIMESTAMP()),
  ('h4d5e6f7-g8h9-7i0j-1k2l-3m4n5o6p7q8r', 'Home Address', 'User physical address for shipping and billing.', PENDING_COMMIT_TIMESTAMP(), PENDING_COMMIT_TIMESTAMP()),
  ('i5e6f7g8-h9i0-8j1k-2l3m-4n5o6p7q8r9s', 'Payment Information', 'User payment details including credit card information.', PENDING_COMMIT_TIMESTAMP(), PENDING_COMMIT_TIMESTAMP()),
  ('j6f7g8h9-i0j1-9k2l-3m4n-5o6p7q8r9s0t', 'IP Address', 'User IP address collected during system access.', PENDING_COMMIT_TIMESTAMP(), PENDING_COMMIT_TIMESTAMP()),
  ('k7g8h9i0-j1k2-0l3m-4n5o-6p7q8r9s0t1u', 'Device ID', 'Unique identifier for user devices accessing the system.', PENDING_COMMIT_TIMESTAMP(), PENDING_COMMIT_TIMESTAMP());

-- 3.4. Seed the DataSubjectTypes table
UPSERT INTO DataSubjectTypes (subject_id, name, description, created_at, updated_at) VALUES
  ('s1a2b3c4-d5e6-4f7g-8h9i-0j1k2l3m4n5o', 'Customer', 'End users who purchase or use our products and services.', PENDING_COMMIT_TIMESTAMP(), PENDING_COMMIT_TIMESTAMP()),
  ('s2b3c4d5-e6f7-5g8h-9i0j-1k2l3m4n5o6p', 'Employee', 'Internal staff members employed by the company.', PENDING_COMMIT_TIMESTAMP(), PENDING_COMMIT_TIMESTAMP()),
  ('s3c4d5e6-f7g8-6h9i-0j1k-2l3m4n5o6p7q', 'Vendor Contact', 'Representatives from third-party service providers.', PENDING_COMMIT_TIMESTAMP(), PENDING_COMMIT_TIMESTAMP()),
  ('s4d5e6f7-g8h9-7i0j-1k2l-3m4n5o6p7q8r', 'Job Applicant', 'Individuals who have applied for employment.', PENDING_COMMIT_TIMESTAMP(), PENDING_COMMIT_TIMESTAMP());

-- 3.5. Seed the DataSubjectTypeElements association table
UPSERT INTO DataSubjectTypeElements (subject_id, element_id, description, created_at, updated_at) VALUES
  ('s1a2b3c4-d5e6-4f7g-8h9i-0j1k2l3m4n5o', 'e1a2b3c4-d5e6-4f7g-8h9i-0j1k2l3m4n5o', 'Customer email addresses for account access and communications.', PENDING_COMMIT_TIMESTAMP(), PENDING_COMMIT_TIMESTAMP()),
  ('s1a2b3c4-d5e6-4f7g-8h9i-0j1k2l3m4n5o', 'f2b3c4d5-e6f7-5g8h-9i0j-1k2l3m4n5o6p', 'Customer full names for account identification.', PENDING_COMMIT_TIMESTAMP(), PENDING_COMMIT_TIMESTAMP()),
  ('s1a2b3c4-d5e6-4f7g-8h9i-0j1k2l3m4n5o', 'g3c4d5e6-f7g8-6h9i-0j1k-2l3m4n5o6p7q', 'Customer phone numbers for account verification and support.', PENDING_COMMIT_TIMESTAMP(), PENDING_COMMIT_TIMESTAMP()),
  ('s1a2b3c4-d5e6-4f7g-8h9i-0j1k2l3m4n5o', 'h4d5e6f7-g8h9-7i0j-1k2l-3m4n5o6p7q8r', 'Customer addresses for product shipping and billing.', PENDING_COMMIT_TIMESTAMP(), PENDING_COMMIT_TIMESTAMP()),
  ('s1a2b3c4-d5e6-4f7g-8h9i-0j1k2l3m4n5o', 'i5e6f7g8-h9i0-8j1k-2l3m-4n5o6p7q8r9s', 'Customer payment information for processing transactions.', PENDING_COMMIT_TIMESTAMP(), PENDING_COMMIT_TIMESTAMP()),
  ('s2b3c4d5-e6f7-5g8h-9i0j-1k2l3m4n5o6p', 'e1a2b3c4-d5e6-4f7g-8h9i-0j1k2l3m4n5o', 'Employee email addresses for work communications.', PENDING_COMMIT_TIMESTAMP(), PENDING_COMMIT_TIMESTAMP()),
  ('s2b3c4d5-e6f7-5g8h-9i0j-1k2l3m4n5o6p', 'f2b3c4d5-e6f7-5g8h-9i0j-1k2l3m4n5o6p', 'Employee full names for HR records.', PENDING_COMMIT_TIMESTAMP(), PENDING_COMMIT_TIMESTAMP()),
  ('s2b3c4d5-e6f7-5g8h-9i0j-1k2l3m4n5o6p', 'g3c4d5e6-f7g8-6h9i-0j1k-2l3m4n5o6p7q', 'Employee phone numbers for contact purposes.', PENDING_COMMIT_TIMESTAMP(), PENDING_COMMIT_TIMESTAMP()),
  ('s2b3c4d5-e6f7-5g8h-9i0j-1k2l3m4n5o6p', 'h4d5e6f7-g8h9-7i0j-1k2l-3m4n5o6p7q8r', 'Employee home addresses for HR records.', PENDING_COMMIT_TIMESTAMP(), PENDING_COMMIT_TIMESTAMP());

-- 3.6. Seed the RelationshipOntology table
UPSERT INTO RelationshipOntology (source_type_id, target_type_id, relationship_type, description, created_at, updated_at) VALUES
  ('8b5f3a0a-9c9a-41f2-8c9a-4a6f9f3c1d0b', '2b6291d5-f623-4a12-8b3a-59d04f145459', 'USES', 'A process uses a system or database.', PENDING_COMMIT_TIMESTAMP(), PENDING_COMMIT_TIMESTAMP()),
  ('2b6291d5-f623-4a12-8b3a-59d04f145459', 'f3a2c5b1-9b1a-4e2b-8d1a-6f3b1a4e2b8d', 'CONTAINS', 'A system contains a category of data.', PENDING_COMMIT_TIMESTAMP(), PENDING_COMMIT_TIMESTAMP()),
  ('2b6291d5-f623-4a12-8b3a-59d04f145459', 'a4e2b8d1-6f3b-4e2b-8d1a-9b1a4e2b8d1a', 'TRANSFERS_DATA_TO', 'A system sends data to a third-party vendor.', PENDING_COMMIT_TIMESTAMP(), PENDING_COMMIT_TIMESTAMP()),
  ('8b5f3a0a-9c9a-41f2-8c9a-4a6f9f3c1d0b', 'a4e2b8d1-6f3b-4e2b-8d1a-9b1a4e2b8d1a', 'ASSISTED_BY', 'A business process is assisted by a vendor.', PENDING_COMMIT_TIMESTAMP(), PENDING_COMMIT_TIMESTAMP()),
  ('2b6291d5-f623-4a12-8b3a-59d04f145459', 'c5b1a4e2-8d1a-4e2b-9b1a-3b1a4e2b8d1a', 'CONTAINS', 'A system contains data about a type of person.', PENDING_COMMIT_TIMESTAMP(), PENDING_COMMIT_TIMESTAMP());

-- 3.7. Add DataSubjectTypeElements to EntityTypes
UPSERT INTO EntityTypes (type_id, name, description, table_name, id_column, created_at, updated_at) VALUES
  ('d7e8f9g0-h1i2-3j4k-5l6m-7n8o9p0q1r2', 'DataSubjectTypeElement', 'Association between a data subject type and a data element.', 'DataSubjectTypeElements', 'subject_id,element_id', PENDING_COMMIT_TIMESTAMP(), PENDING_COMMIT_TIMESTAMP());

-- 3.8. Add Asset to DataSubjectTypeElement relationship
UPSERT INTO RelationshipOntology (source_type_id, target_type_id, relationship_type, description, created_at, updated_at) VALUES
  ('2b6291d5-f623-4a12-8b3a-59d04f145459', 'd7e8f9g0-h1i2-3j4k-5l6m-7n8o9p0q1r2', 'CONTAINS', 'A system contains data about specific types of people.', PENDING_COMMIT_TIMESTAMP(), PENDING_COMMIT_TIMESTAMP());