-- ===================================================================
-- ===== 1. DROP ALL EXISTING TABLES AND INDEXES (DESTRUCTIVE) =====
-- ===================================================================
-- This section clears the database schema to prepare for recreation.
-- The order is important to respect foreign key constraints.

-- Drop indexes first
DROP INDEX IF EXISTS OntologyByRelationshipType;
DROP INDEX IF EXISTS OntologyByTargetType;
DROP INDEX IF EXISTS OntologyBySourceType;
DROP INDEX IF EXISTS EntityTypesByTableName;
DROP INDEX IF EXISTS EntityTypesByName;
DROP INDEX IF EXISTS RelationshipsByTarget;
DROP INDEX IF EXISTS RelationshipsBySource;
DROP INDEX IF EXISTS VendorsByName;
DROP INDEX IF EXISTS DataSubjectTypesByName;
DROP INDEX IF EXISTS DataElementsByName;
DROP INDEX IF EXISTS ProcessingActivitiesByName;
DROP INDEX IF EXISTS AssetsByName;

-- Drop tables with foreign key dependencies
DROP TABLE IF EXISTS EntityTypeProperties;
DROP TABLE IF EXISTS RelationshipOntology;

-- Drop the tables they depended on, and all remaining tables
DROP TABLE IF EXISTS EntityTypes;
DROP TABLE IF EXISTS EntityRelationships;
DROP TABLE IF EXISTS Assets;
DROP TABLE IF EXISTS ProcessingActivities;
DROP TABLE IF EXISTS DataElements;
DROP TABLE IF EXISTS DataSubjectTypes;
DROP TABLE IF EXISTS Vendors;


-- =================================================================
-- ===== 2. CREATE ALL TABLES AND INDEXES (DDL)                =====
-- =================================================================
-- This section rebuilds the entire database schema from scratch.

-- Entity Tables
CREATE TABLE Assets (
    asset_id STRING(36) NOT NULL,
    name STRING(256) NOT NULL,
    description STRING(MAX),
    properties JSON,
    embedding ARRAY<FLOAT64>,
    created_at TIMESTAMP NOT NULL OPTIONS(allow_commit_timestamp=true),
    updated_at TIMESTAMP NOT NULL OPTIONS(allow_commit_timestamp=true)
) PRIMARY KEY (asset_id);

CREATE INDEX AssetsByName ON Assets(name);

CREATE TABLE ProcessingActivities (
    activity_id STRING(36) NOT NULL,
    name STRING(256) NOT NULL,
    description STRING(MAX),
    properties JSON,
    embedding ARRAY<FLOAT64>,
    created_at TIMESTAMP NOT NULL OPTIONS(allow_commit_timestamp=true),
    updated_at TIMESTAMP NOT NULL OPTIONS(allow_commit_timestamp=true)
) PRIMARY KEY (activity_id);

CREATE INDEX ProcessingActivitiesByName ON ProcessingActivities(name);

CREATE TABLE DataElements (
    element_id STRING(36) NOT NULL,
    name STRING(256) NOT NULL,
    description STRING(MAX),
    properties JSON,
    embedding ARRAY<FLOAT64>,
    created_at TIMESTAMP NOT NULL OPTIONS(allow_commit_timestamp=true),
    updated_at TIMESTAMP NOT NULL OPTIONS(allow_commit_timestamp=true)
) PRIMARY KEY (element_id);

CREATE INDEX DataElementsByName ON DataElements(name);

CREATE TABLE DataSubjectTypes (
    subject_id STRING(36) NOT NULL,
    name STRING(256) NOT NULL,
    description STRING(MAX),
    properties JSON,
    embedding ARRAY<FLOAT64>,
    created_at TIMESTAMP NOT NULL OPTIONS(allow_commit_timestamp=true),
    updated_at TIMESTAMP NOT NULL OPTIONS(allow_commit_timestamp=true)
) PRIMARY KEY (subject_id);

CREATE INDEX DataSubjectTypesByName ON DataSubjectTypes(name);

CREATE TABLE Vendors (
    vendor_id STRING(36) NOT NULL,
    name STRING(256) NOT NULL,
    description STRING(MAX),
    properties JSON,
    embedding ARRAY<FLOAT64>,
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

-- Entity Types Table (must be created before tables that reference it)
CREATE TABLE EntityTypes (
    type_id STRING(36) NOT NULL,
    name STRING(128) NOT NULL,
    description STRING(MAX),
    table_name STRING(128) NOT NULL,
    id_column STRING(128) NOT NULL,
    properties JSON,
    created_at TIMESTAMP NOT NULL OPTIONS(allow_commit_timestamp=true),
    updated_at TIMESTAMP NOT NULL OPTIONS(allow_commit_timestamp=true)
) PRIMARY KEY (type_id);

CREATE UNIQUE INDEX EntityTypesByName ON EntityTypes(name);
CREATE INDEX EntityTypesByTableName ON EntityTypes(table_name);

-- Ontology Tables (these have foreign keys referencing EntityTypes)
CREATE TABLE EntityTypeProperties (
    type_id STRING(36) NOT NULL,
    property_name STRING(128) NOT NULL,
    data_type STRING(64) NOT NULL,
    is_required BOOL NOT NULL,
    description STRING(MAX),
    created_at TIMESTAMP NOT NULL OPTIONS(allow_commit_timestamp=true),
    updated_at TIMESTAMP NOT NULL OPTIONS(allow_commit_timestamp=true),
    CONSTRAINT FK_EntityType FOREIGN KEY (type_id) REFERENCES EntityTypes (type_id)
) PRIMARY KEY (type_id, property_name);

CREATE TABLE RelationshipOntology (
    source_type_id STRING(36) NOT NULL,
    target_type_id STRING(36) NOT NULL,
    relationship_type STRING(128) NOT NULL,
    description STRING(MAX),
    properties JSON,
    created_at TIMESTAMP NOT NULL OPTIONS(allow_commit_timestamp=true),
    updated_at TIMESTAMP NOT NULL OPTIONS(allow_commit_timestamp=true),
    CONSTRAINT FK_SourceEntityType FOREIGN KEY (source_type_id) REFERENCES EntityTypes (type_id),
    CONSTRAINT FK_TargetEntityType FOREIGN KEY (target_type_id) REFERENCES EntityTypes (type_id)
) PRIMARY KEY (source_type_id, target_type_id, relationship_type);

CREATE INDEX OntologyBySourceType ON RelationshipOntology(source_type_id);
CREATE INDEX OntologyByTargetType ON RelationshipOntology(target_type_id);
CREATE INDEX OntologyByRelationshipType ON RelationshipOntology(relationship_type);


