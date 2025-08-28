-- =================================================================
-- ===== 3. SEED ONTOLOGY METADATA (DML)                       =====
-- =================================================================
-- This section populates the fresh schema with foundational data.
-- It uses UPSERT to be idempotent.

-- 3.1. Seed the EntityTypes table
INSERT INTO EntityTypes (type_id, name, description, table_name, id_column, created_at, updated_at) VALUES
  ('2b6291d5-f623-4a12-8b3a-59d04f145459', 'Asset', 'A system, application, or database.', 'Assets', 'asset_id', PENDING_COMMIT_TIMESTAMP(), PENDING_COMMIT_TIMESTAMP()),
  ('8b5f3a0a-9c9a-41f2-8c9a-4a6f9f3c1d0b', 'ProcessingActivity', 'A business process that uses data.', 'ProcessingActivities', 'activity_id', PENDING_COMMIT_TIMESTAMP(), PENDING_COMMIT_TIMESTAMP()),
  ('f3a2c5b1-9b1a-4e2b-8d1a-6f3b1a4e2b8d', 'DataElement', 'A specific category of personal data.', 'DataElements', 'element_id', PENDING_COMMIT_TIMESTAMP(), PENDING_COMMIT_TIMESTAMP()),
  ('c5b1a4e2-8d1a-4e2b-9b1a-3b1a4e2b8d1a', 'DataSubjectType', 'A category of individual.', 'DataSubjectTypes', 'subject_id', PENDING_COMMIT_TIMESTAMP(), PENDING_COMMIT_TIMESTAMP()),
  ('a4e2b8d1-6f3b-4e2b-8d1a-9b1a4e2b8d1a', 'Vendor', 'A third-party company or service.', 'Vendors', 'vendor_id', PENDING_COMMIT_TIMESTAMP(), PENDING_COMMIT_TIMESTAMP());

-- 3.2. Seed the EntityTypeProperties table
INSERT INTO EntityTypeProperties (type_id, property_name, data_type, is_required, description, created_at, updated_at) VALUES
  ('2b6291d5-f623-4a12-8b3a-59d04f145459', 'hosting_location', 'STRING', TRUE, 'The physical or cloud region where the asset is hosted.', PENDING_COMMIT_TIMESTAMP(), PENDING_COMMIT_TIMESTAMP()),
  ('2b6291d5-f623-4a12-8b3a-59d04f145459', 'data_retention_days', 'INTEGER', FALSE, 'Number of days data is retained in this asset.', PENDING_COMMIT_TIMESTAMP(), PENDING_COMMIT_TIMESTAMP()),
  ('a4e2b8d1-6f3b-4e2b-8d1a-9b1a4e2b8d1a', 'contact_email', 'STRING', TRUE, 'The primary contact email for the vendor.', PENDING_COMMIT_TIMESTAMP(), PENDING_COMMIT_TIMESTAMP()),
  ('a4e2b8d1-6f3b-4e2b-8d1a-9b1a4e2b8d1a', 'dpa_signed', 'BOOLEAN', FALSE, 'Indicates if a Data Processing Agreement is signed.', PENDING_COMMIT_TIMESTAMP(), PENDING_COMMIT_TIMESTAMP()),
  ('f3a2c5b1-9b1a-4e2b-8d1a-6f3b1a4e2b8d', 'sensitivity_level', 'STRING', TRUE, 'The sensitivity level of the data (e.g., Public, Confidential, Secret).', PENDING_COMMIT_TIMESTAMP(), PENDING_COMMIT_TIMESTAMP());

-- 3.3. Seed the DataElements table
INSERT INTO DataElements (element_id, name, description, created_at, updated_at) VALUES
  -- Identity and Contact Information
  ('e1a2b3c4-d5e6-4f7g-8h9i-0j1k2l3m4n5o', 'Email Address', 'User email address used for account identification and communication.', PENDING_COMMIT_TIMESTAMP(), PENDING_COMMIT_TIMESTAMP()),
  ('f2b3c4d5-e6f7-5g8h-9i0j-1k2l3m4n5o6p', 'Full Name', 'User full name including first and last name.', PENDING_COMMIT_TIMESTAMP(), PENDING_COMMIT_TIMESTAMP()),
  ('g3c4d5e6-f7g8-6h9i-0j1k-2l3m4n5o6p7q', 'Phone Number', 'User phone number for account verification and communication.', PENDING_COMMIT_TIMESTAMP(), PENDING_COMMIT_TIMESTAMP()),
  ('h4d5e6f7-g8h9-7i0j-1k2l-3m4n5o6p7q8r', 'Home Address', 'User physical address for shipping and billing.', PENDING_COMMIT_TIMESTAMP(), PENDING_COMMIT_TIMESTAMP()),
  ('i5e6f7g8-h9i0-8j1k-2l3m-4n5o6p7q8r9s', 'Payment Information', 'User payment details including credit card information.', PENDING_COMMIT_TIMESTAMP(), PENDING_COMMIT_TIMESTAMP()),
  ('j6f7g8h9-i0j1-9k2l-3m4n-5o6p7q8r9s0t', 'IP Address', 'User IP address collected during system access.', PENDING_COMMIT_TIMESTAMP(), PENDING_COMMIT_TIMESTAMP()),
  ('k7g8h9i0-j1k2-0l3m-4n5o-6p7q8r9s0t1u', 'Device ID', 'Unique identifier for user devices accessing the system.', PENDING_COMMIT_TIMESTAMP(), PENDING_COMMIT_TIMESTAMP()),
  ('l8h9i0j1-k2l3-1m4n-5o6p-7q8r9s0t1u2v', 'Username', 'Unique identifier chosen by the user for account access.', PENDING_COMMIT_TIMESTAMP(), PENDING_COMMIT_TIMESTAMP()),
  ('m9i0j1k2-l3m4-2n5o-6p7q-8r9s0t1u2v3w', 'Date of Birth', 'User date of birth for age verification and demographic analysis.', PENDING_COMMIT_TIMESTAMP(), PENDING_COMMIT_TIMESTAMP()),
  ('n0j1k2l3-m4n5-3o6p-7q8r-9s0t1u2v3w4x', 'Social Security Number', 'Government-issued identification number for tax and identity verification.', PENDING_COMMIT_TIMESTAMP(), PENDING_COMMIT_TIMESTAMP()),
  ('o1k2l3m4-n5o6-4p7q-8r9s-0t1u2v3w4x5y', 'Passport Number', 'Government-issued travel document identifier.', PENDING_COMMIT_TIMESTAMP(), PENDING_COMMIT_TIMESTAMP()),
  ('p2l3m4n5-o6p7-5q8r-9s0t-1u2v3w4x5y6z', 'Driver License Number', 'Government-issued driving credential identifier.', PENDING_COMMIT_TIMESTAMP(), PENDING_COMMIT_TIMESTAMP()),
  ('q3m4n5o6-p7q8-6r9s-0t1u-2v3w4x5y6z7a', 'National ID', 'Country-specific national identification number.', PENDING_COMMIT_TIMESTAMP(), PENDING_COMMIT_TIMESTAMP()),
  ('r4n5o6p7-q8r9-7s0t-1u2v-3w4x5y6z7a8b', 'Biometric Data', 'Physical characteristics used for identification including fingerprints, facial recognition, or retinal scans.', PENDING_COMMIT_TIMESTAMP(), PENDING_COMMIT_TIMESTAMP()),
  
  -- Financial Information
  ('s5o6p7q8-r9s0-8t1u-2v3w-4x5y6z7a8b9c', 'Bank Account Number', 'User bank account identifier for financial transactions.', PENDING_COMMIT_TIMESTAMP(), PENDING_COMMIT_TIMESTAMP()),
  ('t6p7q8r9-s0t1-9u2v-3w4x-5y6z7a8b9c0d', 'Credit Score', 'Numerical representation of creditworthiness.', PENDING_COMMIT_TIMESTAMP(), PENDING_COMMIT_TIMESTAMP()),
  ('u7q8r9s0-t1u2-0v3w-4x5y-6z7a8b9c0d1e', 'Tax Identification Number', 'Government-issued number for tax reporting purposes.', PENDING_COMMIT_TIMESTAMP(), PENDING_COMMIT_TIMESTAMP()),
  ('v8r9s0t1-u2v3-1w4x-5y6z-7a8b9c0d1e2f', 'Income Information', 'Details about user income sources and amounts.', PENDING_COMMIT_TIMESTAMP(), PENDING_COMMIT_TIMESTAMP()),
  ('w9s0t1u2-v3w4-2x5y-6z7a-8b9c0d1e2f3g', 'Transaction History', 'Record of financial transactions including purchases and payments.', PENDING_COMMIT_TIMESTAMP(), PENDING_COMMIT_TIMESTAMP()),
  ('x0t1u2v3-w4x5-3y6z-7a8b-9c0d1e2f3g4h', 'Investment Information', 'Details about user investments, portfolios, and financial assets.', PENDING_COMMIT_TIMESTAMP(), PENDING_COMMIT_TIMESTAMP()),
  
  -- Health Information
  ('y1u2v3w4-x5y6-4z7a-8b9c-0d1e2f3g4h5i', 'Medical History', 'Record of past medical conditions, treatments, and procedures.', PENDING_COMMIT_TIMESTAMP(), PENDING_COMMIT_TIMESTAMP()),
  ('z2v3w4x5-y6z7-5a8b-9c0d-1e2f3g4h5i6j', 'Prescription Information', 'Details about medications prescribed to the user.', PENDING_COMMIT_TIMESTAMP(), PENDING_COMMIT_TIMESTAMP()),
  ('a3w4x5y6-z7a8-6b9c-0d1e-2f3g4h5i6j7k', 'Insurance Information', 'Details about user health insurance coverage and policy.', PENDING_COMMIT_TIMESTAMP(), PENDING_COMMIT_TIMESTAMP()),
  ('b4x5y6z7-a8b9-7c0d-1e2f-3g4h5i6j7k8l', 'Genetic Data', 'Information about genetic characteristics and predispositions.', PENDING_COMMIT_TIMESTAMP(), PENDING_COMMIT_TIMESTAMP()),
  ('c5y6z7a8-b9c0-8d1e-2f3g-4h5i6j7k8l9m', 'Vital Signs', 'Measurements of essential body functions like blood pressure, heart rate, and temperature.', PENDING_COMMIT_TIMESTAMP(), PENDING_COMMIT_TIMESTAMP()),
  ('d6z7a8b9-c0d1-9e2f-3g4h-5i6j7k8l9m0n', 'Mental Health Information', 'Data related to psychological conditions, treatments, and therapy.', PENDING_COMMIT_TIMESTAMP(), PENDING_COMMIT_TIMESTAMP()),
  
  -- Online Behavior and Technical Data
  ('e7a8b9c0-d1e2-0f3g-4h5i-6j7k8l9m0n1o', 'Browsing History', 'Record of websites and pages visited by the user.', PENDING_COMMIT_TIMESTAMP(), PENDING_COMMIT_TIMESTAMP()),
  ('f8b9c0d1-e2f3-1g4h-5i6j-7k8l9m0n1o2p', 'Search History', 'Record of search queries made by the user.', PENDING_COMMIT_TIMESTAMP(), PENDING_COMMIT_TIMESTAMP()),
  ('g9c0d1e2-f3g4-2h5i-6j7k-8l9m0n1o2p3q', 'Cookies', 'Small data files stored on user devices to track browsing activity.', PENDING_COMMIT_TIMESTAMP(), PENDING_COMMIT_TIMESTAMP()),
  ('h0d1e2f3-g4h5-3i6j-7k8l-9m0n1o2p3q4r', 'Location Data', 'Geographic coordinates or location information of the user.', PENDING_COMMIT_TIMESTAMP(), PENDING_COMMIT_TIMESTAMP()),
  ('i1e2f3g4-h5i6-4j7k-8l9m-0n1o2p3q4r5s', 'Device Information', 'Details about user hardware, operating system, and browser.', PENDING_COMMIT_TIMESTAMP(), PENDING_COMMIT_TIMESTAMP()),
  ('j2f3g4h5-i6j7-5k8l-9m0n-1o2p3q4r5s6t', 'App Usage Data', 'Information about how users interact with mobile or web applications.', PENDING_COMMIT_TIMESTAMP(), PENDING_COMMIT_TIMESTAMP()),
  
  -- Professional and Educational Information
  ('k3g4h5i6-j7k8-6l9m-0n1o-2p3q4r5s6t7u', 'Employment History', 'Record of past and current employment positions and employers.', PENDING_COMMIT_TIMESTAMP(), PENDING_COMMIT_TIMESTAMP()),
  ('l4h5i6j7-k8l9-7m0n-1o2p-3q4r5s6t7u8v', 'Educational Background', 'Information about academic qualifications, institutions, and achievements.', PENDING_COMMIT_TIMESTAMP(), PENDING_COMMIT_TIMESTAMP()),
  ('m5i6j7k8-l9m0-8n1o-2p3q-4r5s6t7u8v9w', 'Professional Certifications', 'Details about professional qualifications and certifications.', PENDING_COMMIT_TIMESTAMP(), PENDING_COMMIT_TIMESTAMP()),
  ('n6j7k8l9-m0n1-9o2p-3q4r-5s6t7u8v9w0x', 'Performance Reviews', 'Evaluations of work performance and achievements.', PENDING_COMMIT_TIMESTAMP(), PENDING_COMMIT_TIMESTAMP()),
  ('o7k8l9m0-n1o2-0p3q-4r5s-6t7u8v9w0x1y', 'Salary Information', 'Details about compensation, benefits, and financial remuneration.', PENDING_COMMIT_TIMESTAMP(), PENDING_COMMIT_TIMESTAMP()),
  
  -- Preference and Behavioral Data
  ('p8l9m0n1-o2p3-1q4r-5s6t-7u8v9w0x1y2z', 'Purchase History', 'Record of products and services purchased by the user.', PENDING_COMMIT_TIMESTAMP(), PENDING_COMMIT_TIMESTAMP()),
  ('q9m0n1o2-p3q4-2r5s-6t7u-8v9w0x1y2z3a', 'Product Preferences', 'Information about user preferences for specific products or services.', PENDING_COMMIT_TIMESTAMP(), PENDING_COMMIT_TIMESTAMP()),
  ('r0n1o2p3-q4r5-3s6t-7u8v-9w0x1y2z3a4b', 'Marketing Preferences', 'User choices regarding marketing communications and channels.', PENDING_COMMIT_TIMESTAMP(), PENDING_COMMIT_TIMESTAMP()),
  ('s1o2p3q4-r5s6-4t7u-8v9w-0x1y2z3a4b5c', 'Survey Responses', 'Information provided by users in surveys and feedback forms.', PENDING_COMMIT_TIMESTAMP(), PENDING_COMMIT_TIMESTAMP()),
  ('t2p3q4r5-s6t7-5u8v-9w0x-1y2z3a4b5c6d', 'Social Media Activity', 'User interactions, posts, and engagement on social platforms.', PENDING_COMMIT_TIMESTAMP(), PENDING_COMMIT_TIMESTAMP()),
  
  -- Demographic Information
  ('u3q4r5s6-t7u8-6v9w-0x1y-2z3a4b5c6d7e', 'Gender', 'User gender identity information.', PENDING_COMMIT_TIMESTAMP(), PENDING_COMMIT_TIMESTAMP()),
  ('v4r5s6t7-u8v9-7w0x-1y2z-3a4b5c6d7e8f', 'Age', 'User age information derived from date of birth.', PENDING_COMMIT_TIMESTAMP(), PENDING_COMMIT_TIMESTAMP()),
  ('w5s6t7u8-v9w0-8x1y-2z3a-4b5c6d7e8f9g', 'Ethnicity', 'Information about user ethnic background.', PENDING_COMMIT_TIMESTAMP(), PENDING_COMMIT_TIMESTAMP()),
  ('x6t7u8v9-w0x1-9y2z-3a4b-5c6d7e8f9g0h', 'Nationality', 'Information about user country of citizenship.', PENDING_COMMIT_TIMESTAMP(), PENDING_COMMIT_TIMESTAMP()),
  ('y7u8v9w0-x1y2-0z3a-4b5c-6d7e8f9g0h1i', 'Religion', 'Information about user religious beliefs or affiliations.', PENDING_COMMIT_TIMESTAMP(), PENDING_COMMIT_TIMESTAMP()),
  ('z8v9w0x1-y2z3-1a4b-5c6d-7e8f9g0h1i2j', 'Political Opinions', 'Information about user political views or affiliations.', PENDING_COMMIT_TIMESTAMP(), PENDING_COMMIT_TIMESTAMP()),
  ('a9w0x1y2-z3a4-2b5c-6d7e-8f9g0h1i2j3k', 'Sexual Orientation', 'Information about user sexual orientation.', PENDING_COMMIT_TIMESTAMP(), PENDING_COMMIT_TIMESTAMP()),
  ('b0x1y2z3-a4b5-3c6d-7e8f-9g0h1i2j3k4l', 'Marital Status', 'Information about user marriage or relationship status.', PENDING_COMMIT_TIMESTAMP(), PENDING_COMMIT_TIMESTAMP()),
  ('c1y2z3a4-b5c6-4d7e-8f9g-0h1i2j3k4l5m', 'Family Information', 'Details about user family structure, dependents, and relationships.', PENDING_COMMIT_TIMESTAMP(), PENDING_COMMIT_TIMESTAMP());

-- 3.4. Seed the DataSubjectTypes table
INSERT INTO DataSubjectTypes (subject_id, name, description, created_at, updated_at) VALUES
  -- Core Business Relationships
  ('s1a2b3c4-d5e6-4f7g-8h9i-0j1k2l3m4n5o', 'Customer', 'End users who purchase or use our products and services.', PENDING_COMMIT_TIMESTAMP(), PENDING_COMMIT_TIMESTAMP()),
  ('s2b3c4d5-e6f7-5g8h-9i0j-1k2l3m4n5o6p', 'Employee', 'Internal staff members employed by the company.', PENDING_COMMIT_TIMESTAMP(), PENDING_COMMIT_TIMESTAMP()),
  ('s3c4d5e6-f7g8-6h9i-0j1k-2l3m4n5o6p7q', 'Vendor Contact', 'Representatives from third-party service providers.', PENDING_COMMIT_TIMESTAMP(), PENDING_COMMIT_TIMESTAMP()),
  ('s4d5e6f7-g8h9-7i0j-1k2l-3m4n5o6p7q8r', 'Job Applicant', 'Individuals who have applied for employment.', PENDING_COMMIT_TIMESTAMP(), PENDING_COMMIT_TIMESTAMP()),
  ('s5e6f7g8-h9i0-8j1k-2l3m-4n5o6p7q8r9s', 'Business Partner', 'Organizations or individuals with formal business relationships.', PENDING_COMMIT_TIMESTAMP(), PENDING_COMMIT_TIMESTAMP()),
  ('s6f7g8h9-i0j1-9k2l-3m4n-5o6p7q8r9s0t', 'Contractor', 'External individuals providing services under contract.', PENDING_COMMIT_TIMESTAMP(), PENDING_COMMIT_TIMESTAMP()),
  ('s7g8h9i0-j1k2-0l3m-4n5o-6p7q8r9s0t1u', 'Supplier', 'Organizations that provide goods or materials.', PENDING_COMMIT_TIMESTAMP(), PENDING_COMMIT_TIMESTAMP()),
  
  -- Customer Segments
  ('s8h9i0j1-k2l3-1m4n-5o6p-7q8r9s0t1u2v', 'Prospect', 'Potential customers who have shown interest but not yet purchased.', PENDING_COMMIT_TIMESTAMP(), PENDING_COMMIT_TIMESTAMP()),
  ('s9i0j1k2-l3m4-2n5o-6p7q-8r9s0t1u2v3w', 'Former Customer', 'Individuals who previously purchased but are no longer active.', PENDING_COMMIT_TIMESTAMP(), PENDING_COMMIT_TIMESTAMP()),
  ('s0j1k2l3-m4n5-3o6p-7q8r-9s0t1u2v3w4x', 'Subscriber', 'Individuals who have registered for recurring services.', PENDING_COMMIT_TIMESTAMP(), PENDING_COMMIT_TIMESTAMP()),
  ('t1k2l3m4-n5o6-4p7q-8r9s-0t1u2v3w4x5y', 'Trial User', 'Individuals using products or services during a trial period.', PENDING_COMMIT_TIMESTAMP(), PENDING_COMMIT_TIMESTAMP()),
  ('t2l3m4n5-o6p7-5q8r-9s0t-1u2v3w4x5y6z', 'Loyalty Program Member', 'Customers enrolled in loyalty or rewards programs.', PENDING_COMMIT_TIMESTAMP(), PENDING_COMMIT_TIMESTAMP()),
  
  -- Employee Categories
  ('t3m4n5o6-p7q8-6r9s-0t1u-2v3w4x5y6z7a', 'Executive', 'Senior management and leadership team members.', PENDING_COMMIT_TIMESTAMP(), PENDING_COMMIT_TIMESTAMP()),
  ('t4n5o6p7-q8r9-7s0t-1u2v-3w4x5y6z7a8b', 'Manager', 'Employees with supervisory responsibilities.', PENDING_COMMIT_TIMESTAMP(), PENDING_COMMIT_TIMESTAMP()),
  ('t5o6p7q8-r9s0-8t1u-2v3w-4x5y6z7a8b9c', 'Staff', 'Regular employees without management responsibilities.', PENDING_COMMIT_TIMESTAMP(), PENDING_COMMIT_TIMESTAMP()),
  ('t6p7q8r9-s0t1-9u2v-3w4x-5y6z7a8b9c0d', 'Intern', 'Temporary employees gaining work experience.', PENDING_COMMIT_TIMESTAMP(), PENDING_COMMIT_TIMESTAMP()),
  ('t7q8r9s0-t1u2-0v3w-4x5y-6z7a8b9c0d1e', 'Former Employee', 'Individuals who previously worked for the organization.', PENDING_COMMIT_TIMESTAMP(), PENDING_COMMIT_TIMESTAMP()),
  ('t8r9s0t1-u2v3-1w4x-5y6z-7a8b9c0d1e2f', 'Remote Worker', 'Employees who work primarily outside company facilities.', PENDING_COMMIT_TIMESTAMP(), PENDING_COMMIT_TIMESTAMP()),
  
  -- Healthcare Specific
  ('t9s0t1u2-v3w4-2x5y-6z7a-8b9c0d1e2f3g', 'Patient', 'Individuals receiving medical care or treatment.', PENDING_COMMIT_TIMESTAMP(), PENDING_COMMIT_TIMESTAMP()),
  ('u0t1u2v3-w4x5-3y6z-7a8b-9c0d1e2f3g4h', 'Healthcare Provider', 'Medical professionals providing healthcare services.', PENDING_COMMIT_TIMESTAMP(), PENDING_COMMIT_TIMESTAMP()),
  ('u1u2v3w4-x5y6-4z7a-8b9c-0d1e2f3g4h5i', 'Insurance Beneficiary', 'Individuals covered by health insurance policies.', PENDING_COMMIT_TIMESTAMP(), PENDING_COMMIT_TIMESTAMP()),
  ('u2v3w4x5-y6z7-5a8b-9c0d-1e2f3g4h5i6j', 'Medical Research Subject', 'Individuals participating in clinical trials or medical research.', PENDING_COMMIT_TIMESTAMP(), PENDING_COMMIT_TIMESTAMP()),
  
  -- Financial Services Specific
  ('u3w4x5y6-z7a8-6b9c-0d1e-2f3g4h5i6j7k', 'Account Holder', 'Individuals with financial accounts at the institution.', PENDING_COMMIT_TIMESTAMP(), PENDING_COMMIT_TIMESTAMP()),
  ('u4x5y6z7-a8b9-7c0d-1e2f-3g4h5i6j7k8l', 'Loan Applicant', 'Individuals who have applied for credit or loans.', PENDING_COMMIT_TIMESTAMP(), PENDING_COMMIT_TIMESTAMP()),
  ('u5y6z7a8-b9c0-8d1e-2f3g-4h5i6j7k8l9m', 'Borrower', 'Individuals who have active loans or credit.', PENDING_COMMIT_TIMESTAMP(), PENDING_COMMIT_TIMESTAMP()),
  ('u6z7a8b9-c0d1-9e2f-3g4h-5i6j7k8l9m0n', 'Investor', 'Individuals who have invested funds with the institution.', PENDING_COMMIT_TIMESTAMP(), PENDING_COMMIT_TIMESTAMP()),
  ('u7a8b9c0-d1e2-0f3g-4h5i-6j7k8l9m0n1o', 'Guarantor', 'Individuals who have guaranteed loans for others.', PENDING_COMMIT_TIMESTAMP(), PENDING_COMMIT_TIMESTAMP()),
  
  -- Education Specific
  ('u8b9c0d1-e2f3-1g4h-5i6j-7k8l9m0n1o2p', 'Student', 'Individuals enrolled in educational programs.', PENDING_COMMIT_TIMESTAMP(), PENDING_COMMIT_TIMESTAMP()),
  ('u9c0d1e2-f3g4-2h5i-6j7k-8l9m0n1o2p3q', 'Parent/Guardian', 'Individuals responsible for students under legal age.', PENDING_COMMIT_TIMESTAMP(), PENDING_COMMIT_TIMESTAMP()),
  ('v0d1e2f3-g4h5-3i6j-7k8l-9m0n1o2p3q4r', 'Faculty', 'Teachers, professors, and instructional staff.', PENDING_COMMIT_TIMESTAMP(), PENDING_COMMIT_TIMESTAMP()),
  ('v1e2f3g4-h5i6-4j7k-8l9m-0n1o2p3q4r5s', 'Alumni', 'Former students who have completed educational programs.', PENDING_COMMIT_TIMESTAMP(), PENDING_COMMIT_TIMESTAMP()),
  
  -- E-commerce and Retail Specific
  ('v2f3g4h5-i6j7-5k8l-9m0n-1o2p3q4r5s6t', 'Online Shopper', 'Individuals who browse or purchase through digital channels.', PENDING_COMMIT_TIMESTAMP(), PENDING_COMMIT_TIMESTAMP()),
  ('v3g4h5i6-j7k8-6l9m-0n1o-2p3q4r5s6t7u', 'In-Store Customer', 'Individuals who shop at physical retail locations.', PENDING_COMMIT_TIMESTAMP(), PENDING_COMMIT_TIMESTAMP()),
  ('v4h5i6j7-k8l9-7m0n-1o2p-3q4r5s6t7u8v', 'Gift Recipient', 'Individuals who receive products purchased by others.', PENDING_COMMIT_TIMESTAMP(), PENDING_COMMIT_TIMESTAMP()),
  
  -- Technology and Online Services
  ('v5i6j7k8-l9m0-8n1o-2p3q-4r5s6t7u8v9w', 'Website Visitor', 'Individuals who browse websites without creating accounts.', PENDING_COMMIT_TIMESTAMP(), PENDING_COMMIT_TIMESTAMP()),
  ('v6j7k8l9-m0n1-9o2p-3q4r-5s6t7u8v9w0x', 'App User', 'Individuals who use mobile or desktop applications.', PENDING_COMMIT_TIMESTAMP(), PENDING_COMMIT_TIMESTAMP()),
  ('v7k8l9m0-n1o2-0p3q-4r5s-6t7u8v9w0x1y', 'Content Creator', 'Individuals who generate content on platforms.', PENDING_COMMIT_TIMESTAMP(), PENDING_COMMIT_TIMESTAMP()),
  ('v8l9m0n1-o2p3-1q4r-5s6t-7u8v9w0x1y2z', 'Beta Tester', 'Individuals who test pre-release products or features.', PENDING_COMMIT_TIMESTAMP(), PENDING_COMMIT_TIMESTAMP()),
  
  -- Special Categories
  ('v9m0n1o2-p3q4-2r5s-6t7u-8v9w0x1y2z3a', 'Minor', 'Individuals under the legal age of majority.', PENDING_COMMIT_TIMESTAMP(), PENDING_COMMIT_TIMESTAMP()),
  ('w0n1o2p3-q4r5-3s6t-7u8v-9w0x1y2z3a4b', 'Vulnerable Individual', 'Persons requiring special protections due to capacity or circumstances.', PENDING_COMMIT_TIMESTAMP(), PENDING_COMMIT_TIMESTAMP()),
  ('w1o2p3q4-r5s6-4t7u-8v9w-0x1y2z3a4b5c', 'Authorized Representative', 'Individuals legally authorized to act on behalf of others.', PENDING_COMMIT_TIMESTAMP(), PENDING_COMMIT_TIMESTAMP()),
  ('w2p3q4r5-s6t7-5u8v-9w0x-1y2z3a4b5c6d', 'Data Subject Representative', 'Individuals exercising rights on behalf of data subjects.', PENDING_COMMIT_TIMESTAMP(), PENDING_COMMIT_TIMESTAMP());

-- 3.5. Seed the DataSubjectTypeElements association table
INSERT INTO DataSubjectTypeElements (subject_id, element_id, description, created_at, updated_at) VALUES
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
INSERT INTO RelationshipOntology (source_type_id, target_type_id, relationship_type, description, created_at, updated_at) VALUES
  ('8b5f3a0a-9c9a-41f2-8c9a-4a6f9f3c1d0b', '2b6291d5-f623-4a12-8b3a-59d04f145459', 'USES', 'A process uses a system or database.', PENDING_COMMIT_TIMESTAMP(), PENDING_COMMIT_TIMESTAMP()),
  ('2b6291d5-f623-4a12-8b3a-59d04f145459', 'f3a2c5b1-9b1a-4e2b-8d1a-6f3b1a4e2b8d', 'CONTAINS', 'A system contains a category of data.', PENDING_COMMIT_TIMESTAMP(), PENDING_COMMIT_TIMESTAMP()),
  ('2b6291d5-f623-4a12-8b3a-59d04f145459', 'a4e2b8d1-6f3b-4e2b-8d1a-9b1a4e2b8d1a', 'TRANSFERS_DATA_TO', 'A system sends data to a third-party vendor.', PENDING_COMMIT_TIMESTAMP(), PENDING_COMMIT_TIMESTAMP()),
  ('8b5f3a0a-9c9a-41f2-8c9a-4a6f9f3c1d0b', 'a4e2b8d1-6f3b-4e2b-8d1a-9b1a4e2b8d1a', 'ASSISTED_BY', 'A business process is assisted by a vendor.', PENDING_COMMIT_TIMESTAMP(), PENDING_COMMIT_TIMESTAMP()),
  ('2b6291d5-f623-4a12-8b3a-59d04f145459', 'c5b1a4e2-8d1a-4e2b-9b1a-3b1a4e2b8d1a', 'CONTAINS', 'A system contains data about a type of person.', PENDING_COMMIT_TIMESTAMP(), PENDING_COMMIT_TIMESTAMP());

-- 3.7. Add DataSubjectTypeElements to EntityTypes
INSERT INTO EntityTypes (type_id, name, description, table_name, id_column, created_at, updated_at) VALUES
  ('d7e8f9g0-h1i2-3j4k-5l6m-7n8o9p0q1r2', 'DataSubjectTypeElement', 'Association between a data subject type and a data element.', 'DataSubjectTypeElements', 'subject_id,element_id', PENDING_COMMIT_TIMESTAMP(), PENDING_COMMIT_TIMESTAMP());

-- 3.8. Add Asset to DataSubjectTypeElement relationship
INSERT INTO RelationshipOntology (source_type_id, target_type_id, relationship_type, description, created_at, updated_at) VALUES
  ('2b6291d5-f623-4a12-8b3a-59d04f145459', 'd7e8f9g0-h1i2-3j4k-5l6m-7n8o9p0q1r2', 'CONTAINS', 'A system contains data about specific types of people.', PENDING_COMMIT_TIMESTAMP(), PENDING_COMMIT_TIMESTAMP());