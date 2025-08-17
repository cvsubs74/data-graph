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

-- 3.3. Seed the RelationshipOntology table
UPSERT INTO RelationshipOntology (source_type_id, target_type_id, relationship_type, description, created_at, updated_at) VALUES
  ('8b5f3a0a-9c9a-41f2-8c9a-4a6f9f3c1d0b', '2b6291d5-f623-4a12-8b3a-59d04f145459', 'USES', 'A process uses a system or database.', PENDING_COMMIT_TIMESTAMP(), PENDING_COMMIT_TIMESTAMP()),
  ('2b6291d5-f623-4a12-8b3a-59d04f145459', 'f3a2c5b1-9b1a-4e2b-8d1a-6f3b1a4e2b8d', 'CONTAINS', 'A system contains a category of data.', PENDING_COMMIT_TIMESTAMP(), PENDING_COMMIT_TIMESTAMP()),
  ('2b6291d5-f623-4a12-8b3a-59d04f145459', 'a4e2b8d1-6f3b-4e2b-8d1a-9b1a4e2b8d1a', 'TRANSFERS_DATA_TO', 'A system sends data to a third-party vendor.', PENDING_COMMIT_TIMESTAMP(), PENDING_COMMIT_TIMESTAMP()),
  ('8b5f3a0a-9c9a-41f2-8c9a-4a6f9f3c1d0b', 'a4e2b8d1-6f3b-4e2b-8d1a-9b1a4e2b8d1a', 'ASSISTED_BY', 'A business process is assisted by a vendor.', PENDING_COMMIT_TIMESTAMP(), PENDING_COMMIT_TIMESTAMP()),
  ('f3a2c5b1-9b1a-4e2b-8d1a-6f3b1a4e2b8d', 'c5b1a4e2-8d1a-4e2b-9b1a-3b1a4e2b8d1a', 'DESCRIBES', 'A piece of data describes a type of person.', PENDING_COMMIT_TIMESTAMP(), PENDING_COMMIT_TIMESTAMP());