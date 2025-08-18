import os
import json
import uuid
import numpy as np

import vertexai
from vertexai.generative_models import GenerativeModel
from vertexai.preview.language_models import TextEmbeddingModel

from google.cloud import spanner, secretmanager
from google.cloud.spanner_v1 import param_types

class DataGraphService:
    """A service class to manage all interactions with the data graph.

    This includes initializing GCP clients, ingesting documents, and answering
    questions by querying the Spanner database and using Vertex AI models.
    """

    def __init__(self):
        """Initializes all necessary GCP clients and configurations."""
        # Initialize with None values first
        self.database = None
        self.embedding_model = None
        self.project_id = None
        self.location = None
        
        try:
            # Get project ID from environment
            self.project_id = os.environ.get("GCP_PROJECT")
            if not self.project_id:
                raise ValueError("GCP_PROJECT environment variable not set.")
            
            print(f"Initializing DataGraphService with project ID: {self.project_id}")
            
            # Initialize Vertex AI with explicit project and location
            self.location = "us-central1"
            vertexai.init(project=self.project_id, location=self.location)
            print(f"Vertex AI initialized with project {self.project_id} and location {self.location}")
            
            # Initialize Gemini embedding model
            try:
                self.embedding_model = TextEmbeddingModel.from_pretrained("text-embedding-004")
                # Test the model using the correct method name: embed_content
                test_response = self.embedding_model.get_embeddings(["Test embedding"])
                print("Gemini embedding model initialized and tested successfully.")
            except Exception as model_error:
                print(f"ERROR: Failed to initialize embedding model: {model_error}")
                raise

            # Initialize database connection
            try:
                secret_client = secretmanager.SecretManagerServiceClient()
                
                def get_secret(secret_id):
                    name = f"projects/{self.project_id}/secrets/{secret_id}/versions/latest"
                    response = secret_client.access_secret_version(request={"name": name})
                    return response.payload.data.decode("UTF-8")

                spanner_instance_id = get_secret("spanner-instance-id")
                spanner_database_id = get_secret("spanner-database-id")
                print(f"Retrieved Spanner configuration: instance={spanner_instance_id}, database={spanner_database_id}")

                spanner_client = spanner.Client(project=self.project_id)
                instance = spanner_client.instance(spanner_instance_id)
                self.database = instance.database(spanner_database_id)
                print("Spanner database connection initialized successfully.")
            except Exception as db_error:
                print(f"ERROR: Failed to initialize database connection: {db_error}")
                raise
                
            print("DataGraphService initialization completed successfully.")

        except Exception as e:
            print(f"FATAL: Could not initialize DataGraphService: {e}")
            # Ensure all components are set to None if initialization fails
            self.database = None
            self.embedding_model = None

    def is_initialized(self) -> bool:
        """Check if the service is properly initialized."""
        return self.database is not None and self.embedding_model is not None

    # ===== SIMILARITY SEARCH =====

    def _generate_embedding(self, name: str, description: str) -> list[float]:
        """Generates a vector embedding from an entity's name and description using Gemini."""
        text_to_embed = f"Name: {name}. Description: {description or ''}"
        # Get embeddings from the model
        response = self.embedding_model.get_embeddings([text_to_embed])
        
        # Extract the values from the TextEmbedding object
        if hasattr(response[0], 'values'):
            # For text-embedding-004 model
            return response[0].values
        elif isinstance(response, list) and len(response) > 0:
            # Handle different response formats
            if isinstance(response[0], list):
                return response[0]
            else:
                # Try to convert the embedding object to a list
                try:
                    return list(response[0])
                except:
                    raise ValueError(f"Unable to extract embedding values from response: {type(response)}")
        else:
            raise ValueError(f"Unexpected embedding response format: {type(response)}")


    def find_similar_entities(self, table_name: str, id_column: str, name: str, description: str, limit: int = 5) -> list[dict]:
        """Finds semantically similar entities in a specified table."""
        allowed_tables = {"Assets", "Vendors", "ProcessingActivities", "DataElements", "DataSubjectTypes"}
        if table_name not in allowed_tables:
            raise ValueError(f"Invalid table name for search: {table_name}")

        query_embedding = self._generate_embedding(name, description)
        
        with self.database.snapshot() as snapshot:
            sql = f"""
                SELECT
                    {id_column},
                    name,
                    description,
                    COSINE_DISTANCE(embedding, @query_embedding) AS distance
                FROM {table_name}
                WHERE embedding IS NOT NULL
                ORDER BY distance
                LIMIT @limit
            """
            
            params = {"query_embedding": query_embedding, "limit": limit}
            param_types_dict = {"query_embedding": param_types.Array(param_types.FLOAT64), "limit": param_types.INT64}
            
            results = list(snapshot.execute_sql(sql, params=params, param_types=param_types_dict))
            
            similar_entities = []
            for row in results:
                similar_entities.append({
                    "id": row[0],
                    "name": row[1],
                    "description": row[2],
                    "similarity_distance": row[3]
                })
            return similar_entities

    # ===== CRUD OPERATIONS FOR ASSETS =====
    
    def create_asset(self, name: str, description: str = None, properties: dict = None) -> str:
        """Create a new asset, generate its embedding, and return its ID."""
        asset_id = str(uuid.uuid4())
        properties_json = json.dumps(properties) if properties else None
        embedding = self._generate_embedding(name, description)
        
        def insert_asset(transaction):
            transaction.insert(
                table="Assets",
                columns=("asset_id", "name", "description", "properties", "embedding", "created_at", "updated_at"),
                values=[(asset_id, name, description, properties_json, embedding, spanner.COMMIT_TIMESTAMP, spanner.COMMIT_TIMESTAMP)]
            )
        
        try:
            self.database.run_in_transaction(insert_asset)
            return asset_id
        except Exception as e:
            print(f"Error creating asset: {e}")
            return ""

    def get_asset(self, asset_id: str) -> dict:
        """Retrieve an asset by ID."""
        with self.database.snapshot() as snapshot:
            sql = "SELECT asset_id, name, description, properties, created_at, updated_at FROM Assets WHERE asset_id = @asset_id"
            results = list(snapshot.execute_sql(sql, params={"asset_id": asset_id}, param_types={"asset_id": param_types.STRING}))
            
            if not results:
                return None
            
            row = results[0]
            return {
                "asset_id": row[0],
                "name": row[1],
                "description": row[2],
                "properties": row[3],
                "created_at": row[4].isoformat() if row[4] else None,
                "updated_at": row[5].isoformat() if row[5] else None
            }

    def update_asset(self, asset_id: str, name: str = None, description: str = None, properties: dict = None) -> bool:
        """Update an asset. Re-calculates embedding if name or description changes."""
        def update_asset_txn(transaction):
            updates = []
            params = {"asset_id": asset_id}
            param_types_dict = {"asset_id": param_types.STRING}
            
            if name is not None or description is not None:
                read_sql = "SELECT name, description FROM Assets WHERE asset_id = @asset_id"
                current_values = list(transaction.execute_sql(read_sql, params=params, param_types=param_types_dict))
                if not current_values: return
                
                current_name, current_desc = current_values[0]
                final_name = name if name is not None else current_name
                final_desc = description if description is not None else current_desc
                new_embedding = self._generate_embedding(final_name, final_desc)

                updates.append("embedding = @embedding")
                params["embedding"] = new_embedding
                param_types_dict["embedding"] = param_types.Array(param_types.FLOAT64)

            if name is not None:
                updates.append("name = @name")
                params["name"] = name
                param_types_dict["name"] = param_types.STRING
            if description is not None:
                updates.append("description = @description")
                params["description"] = description
                param_types_dict["description"] = param_types.STRING
            if properties is not None:
                updates.append("properties = @properties")
                params["properties"] = json.dumps(properties)
                param_types_dict["properties"] = param_types.JSON
            
            if not updates: return
            
            updates.append("updated_at = @updated_at")
            params["updated_at"] = spanner.COMMIT_TIMESTAMP
            param_types_dict["updated_at"] = param_types.TIMESTAMP
            
            sql = f"UPDATE Assets SET {', '.join(updates)} WHERE asset_id = @asset_id"
            transaction.execute_update(sql, params=params, param_types=param_types_dict)
        
        try:
            self.database.run_in_transaction(update_asset_txn)
            return True
        except Exception as e:
            print(f"Error updating asset: {e}")
            return False

    def delete_asset(self, asset_id: str) -> bool:
        """Delete an asset and its relationships. Returns True if successful."""
        def delete_asset_txn(transaction):
            transaction.execute_update(
                "DELETE FROM EntityRelationships WHERE source_id = @asset_id OR target_id = @asset_id",
                params={"asset_id": asset_id}, param_types={"asset_id": param_types.STRING}
            )
            transaction.execute_update(
                "DELETE FROM Assets WHERE asset_id = @asset_id",
                params={"asset_id": asset_id}, param_types={"asset_id": param_types.STRING}
            )
        
        try:
            self.database.run_in_transaction(delete_asset_txn)
            return True
        except Exception as e:
            print(f"Error deleting asset: {e}")
            return False

    def list_assets(self, limit: int = 100) -> list:
        """List all assets."""
        with self.database.snapshot() as snapshot:
            sql = "SELECT asset_id, name, description, properties, created_at, updated_at FROM Assets ORDER BY name LIMIT @limit"
            results = snapshot.execute_sql(sql, params={"limit": limit}, param_types={"limit": param_types.INT64})
            return [{
                "asset_id": row[0], "name": row[1], "description": row[2], "properties": row[3],
                "created_at": row[4].isoformat() if row[4] else None, "updated_at": row[5].isoformat() if row[5] else None
            } for row in results]

    # ===== CRUD OPERATIONS FOR PROCESSING ACTIVITIES =====
    
    def create_processing_activity(self, name: str, description: str = None, properties: dict = None) -> str:
        """Create a new processing activity, generate its embedding, and return its ID."""
        activity_id = str(uuid.uuid4())
        properties_json = json.dumps(properties) if properties else None
        embedding = self._generate_embedding(name, description)
        
        def insert_activity(transaction):
            transaction.insert(
                table="ProcessingActivities",
                columns=("activity_id", "name", "description", "properties", "embedding", "created_at", "updated_at"),
                values=[(activity_id, name, description, properties_json, embedding, spanner.COMMIT_TIMESTAMP, spanner.COMMIT_TIMESTAMP)]
            )
        
        try:
            self.database.run_in_transaction(insert_activity)
            return activity_id
        except Exception as e:
            print(f"Error creating processing activity: {e}")
            return ""

    def get_processing_activity(self, activity_id: str) -> dict:
        """Retrieve a processing activity by ID."""
        with self.database.snapshot() as snapshot:
            sql = "SELECT activity_id, name, description, properties, created_at, updated_at FROM ProcessingActivities WHERE activity_id = @activity_id"
            results = list(snapshot.execute_sql(sql, params={"activity_id": activity_id}, param_types={"activity_id": param_types.STRING}))
            if not results: return None
            row = results[0]
            return {
                "activity_id": row[0], "name": row[1], "description": row[2], "properties": row[3],
                "created_at": row[4].isoformat() if row[4] else None, "updated_at": row[5].isoformat() if row[5] else None
            }

    def update_processing_activity(self, activity_id: str, name: str = None, description: str = None, properties: dict = None) -> bool:
        """Update a processing activity. Re-calculates embedding if name or description changes."""
        def update_activity_txn(transaction):
            updates = []
            params = {"activity_id": activity_id}
            param_types_dict = {"activity_id": param_types.STRING}
            
            if name is not None or description is not None:
                read_sql = "SELECT name, description FROM ProcessingActivities WHERE activity_id = @activity_id"
                current_values = list(transaction.execute_sql(read_sql, params=params, param_types=param_types_dict))
                if not current_values: return
                
                current_name, current_desc = current_values[0]
                final_name = name if name is not None else current_name
                final_desc = description if description is not None else current_desc
                new_embedding = self._generate_embedding(final_name, final_desc)
                
                updates.append("embedding = @embedding")
                params["embedding"] = new_embedding
                param_types_dict["embedding"] = param_types.Array(param_types.FLOAT64)

            if name is not None:
                updates.append("name = @name")
                params["name"] = name
                param_types_dict["name"] = param_types.STRING
            if description is not None:
                updates.append("description = @description")
                params["description"] = description
                param_types_dict["description"] = param_types.STRING
            if properties is not None:
                updates.append("properties = @properties")
                params["properties"] = json.dumps(properties)
                param_types_dict["properties"] = param_types.JSON
            
            if not updates: return
            
            updates.append("updated_at = @updated_at")
            params["updated_at"] = spanner.COMMIT_TIMESTAMP
            param_types_dict["updated_at"] = param_types.TIMESTAMP
            
            sql = f"UPDATE ProcessingActivities SET {', '.join(updates)} WHERE activity_id = @activity_id"
            transaction.execute_update(sql, params=params, param_types=param_types_dict)
        
        try:
            self.database.run_in_transaction(update_activity_txn)
            return True
        except Exception as e:
            print(f"Error updating processing activity: {e}")
            return False

    def delete_processing_activity(self, activity_id: str) -> bool:
        """Delete a processing activity and its relationships."""
        def delete_activity_txn(transaction):
            transaction.execute_update(
                "DELETE FROM EntityRelationships WHERE source_id = @activity_id OR target_id = @activity_id",
                params={"activity_id": activity_id}, param_types={"activity_id": param_types.STRING}
            )
            transaction.execute_update(
                "DELETE FROM ProcessingActivities WHERE activity_id = @activity_id",
                params={"activity_id": activity_id}, param_types={"activity_id": param_types.STRING}
            )
        try:
            self.database.run_in_transaction(delete_activity_txn)
            return True
        except Exception as e:
            print(f"Error deleting processing activity: {e}")
            return False

    def list_processing_activities(self, limit: int = 100) -> list:
        """List all processing activities."""
        with self.database.snapshot() as snapshot:
            sql = "SELECT activity_id, name, description, properties, created_at, updated_at FROM ProcessingActivities ORDER BY name LIMIT @limit"
            results = snapshot.execute_sql(sql, params={"limit": limit}, param_types={"limit": param_types.INT64})
            return [{
                "activity_id": row[0], "name": row[1], "description": row[2], "properties": row[3],
                "created_at": row[4].isoformat() if row[4] else None, "updated_at": row[5].isoformat() if row[5] else None
            } for row in results]

    # ===== CRUD OPERATIONS FOR DATA ELEMENTS =====
    
    def create_data_element(self, name: str, description: str = None, properties: dict = None) -> str:
        """Create a new data element, generate its embedding, and return its ID."""
        element_id = str(uuid.uuid4())
        properties_json = json.dumps(properties) if properties else None
        embedding = self._generate_embedding(name, description)
        
        def insert_element(transaction):
            transaction.insert(
                table="DataElements",
                columns=("element_id", "name", "description", "properties", "embedding", "created_at", "updated_at"),
                values=[(element_id, name, description, properties_json, embedding, spanner.COMMIT_TIMESTAMP, spanner.COMMIT_TIMESTAMP)]
            )
        
        try:
            self.database.run_in_transaction(insert_element)
            return element_id
        except Exception as e:
            print(f"Error creating data element: {e}")
            return ""

    def get_data_element(self, element_id: str) -> dict:
        """Retrieve a data element by ID."""
        with self.database.snapshot() as snapshot:
            sql = "SELECT element_id, name, description, properties, created_at, updated_at FROM DataElements WHERE element_id = @element_id"
            results = list(snapshot.execute_sql(sql, params={"element_id": element_id}, param_types={"element_id": param_types.STRING}))
            if not results: return None
            row = results[0]
            return {
                "element_id": row[0], "name": row[1], "description": row[2], "properties": row[3],
                "created_at": row[4].isoformat() if row[4] else None, "updated_at": row[5].isoformat() if row[5] else None
            }

    def update_data_element(self, element_id: str, name: str = None, description: str = None, properties: dict = None) -> bool:
        """Update a data element. Re-calculates embedding if name or description changes."""
        def update_element_txn(transaction):
            updates = []
            params = {"element_id": element_id}
            param_types_dict = {"element_id": param_types.STRING}
            
            if name is not None or description is not None:
                read_sql = "SELECT name, description FROM DataElements WHERE element_id = @element_id"
                current_values = list(transaction.execute_sql(read_sql, params=params, param_types=param_types_dict))
                if not current_values: return
                
                current_name, current_desc = current_values[0]
                final_name = name if name is not None else current_name
                final_desc = description if description is not None else current_desc
                new_embedding = self._generate_embedding(final_name, final_desc)

                updates.append("embedding = @embedding")
                params["embedding"] = new_embedding
                param_types_dict["embedding"] = param_types.Array(param_types.FLOAT64)

            if name is not None:
                updates.append("name = @name")
                params["name"] = name
                param_types_dict["name"] = param_types.STRING
            if description is not None:
                updates.append("description = @description")
                params["description"] = description
                param_types_dict["description"] = param_types.STRING
            if properties is not None:
                updates.append("properties = @properties")
                params["properties"] = json.dumps(properties)
                param_types_dict["properties"] = param_types.JSON
            
            if not updates: return
            
            updates.append("updated_at = @updated_at")
            params["updated_at"] = spanner.COMMIT_TIMESTAMP
            param_types_dict["updated_at"] = param_types.TIMESTAMP
            
            sql = f"UPDATE DataElements SET {', '.join(updates)} WHERE element_id = @element_id"
            transaction.execute_update(sql, params=params, param_types=param_types_dict)
        
        try:
            self.database.run_in_transaction(update_element_txn)
            return True
        except Exception as e:
            print(f"Error updating data element: {e}")
            return False

    def delete_data_element(self, element_id: str) -> bool:
        """Delete a data element and its relationships."""
        def delete_element_txn(transaction):
            transaction.execute_update(
                "DELETE FROM EntityRelationships WHERE source_id = @element_id OR target_id = @element_id",
                params={"element_id": element_id}, param_types={"element_id": param_types.STRING}
            )
            transaction.execute_update(
                "DELETE FROM DataElements WHERE element_id = @element_id",
                params={"element_id": element_id}, param_types={"element_id": param_types.STRING}
            )
        try:
            self.database.run_in_transaction(delete_element_txn)
            return True
        except Exception as e:
            print(f"Error deleting data element: {e}")
            return False

    def list_data_elements(self, limit: int = 100) -> list:
        """List all data elements."""
        with self.database.snapshot() as snapshot:
            sql = "SELECT element_id, name, description, properties, created_at, updated_at FROM DataElements ORDER BY name LIMIT @limit"
            results = snapshot.execute_sql(sql, params={"limit": limit}, param_types={"limit": param_types.INT64})
            return [{
                "element_id": row[0], "name": row[1], "description": row[2], "properties": row[3],
                "created_at": row[4].isoformat() if row[4] else None, "updated_at": row[5].isoformat() if row[5] else None
            } for row in results]

    # ===== CRUD OPERATIONS FOR DATA SUBJECT TYPES =====
    
    def create_data_subject_type(self, name: str, description: str = None, properties: dict = None) -> str:
        """Create a new data subject type, generate its embedding, and return its ID."""
        subject_id = str(uuid.uuid4())
        properties_json = json.dumps(properties) if properties else None
        embedding = self._generate_embedding(name, description)
        
        def insert_subject(transaction):
            transaction.insert(
                table="DataSubjectTypes",
                columns=("subject_id", "name", "description", "properties", "embedding", "created_at", "updated_at"),
                values=[(subject_id, name, description, properties_json, embedding, spanner.COMMIT_TIMESTAMP, spanner.COMMIT_TIMESTAMP)]
            )
        
        try:
            self.database.run_in_transaction(insert_subject)
            return subject_id
        except Exception as e:
            print(f"Error creating data subject type: {e}")
            return ""

    def get_data_subject_type(self, subject_id: str) -> dict:
        """Retrieve a data subject type by ID."""
        with self.database.snapshot() as snapshot:
            sql = "SELECT subject_id, name, description, properties, created_at, updated_at FROM DataSubjectTypes WHERE subject_id = @subject_id"
            results = list(snapshot.execute_sql(sql, params={"subject_id": subject_id}, param_types={"subject_id": param_types.STRING}))
            if not results: return None
            row = results[0]
            return {
                "subject_id": row[0], "name": row[1], "description": row[2], "properties": row[3],
                "created_at": row[4].isoformat() if row[4] else None, "updated_at": row[5].isoformat() if row[5] else None
            }

    def update_data_subject_type(self, subject_id: str, name: str = None, description: str = None, properties: dict = None) -> bool:
        """Update a data subject type. Re-calculates embedding if name or description changes."""
        def update_subject_txn(transaction):
            updates = []
            params = {"subject_id": subject_id}
            param_types_dict = {"subject_id": param_types.STRING}
            
            if name is not None or description is not None:
                read_sql = "SELECT name, description FROM DataSubjectTypes WHERE subject_id = @subject_id"
                current_values = list(transaction.execute_sql(read_sql, params=params, param_types=param_types_dict))
                if not current_values: return
                
                current_name, current_desc = current_values[0]
                final_name = name if name is not None else current_name
                final_desc = description if description is not None else current_desc
                new_embedding = self._generate_embedding(final_name, final_desc)

                updates.append("embedding = @embedding")
                params["embedding"] = new_embedding
                param_types_dict["embedding"] = param_types.Array(param_types.FLOAT64)

            if name is not None:
                updates.append("name = @name")
                params["name"] = name
                param_types_dict["name"] = param_types.STRING
            if description is not None:
                updates.append("description = @description")
                params["description"] = description
                param_types_dict["description"] = param_types.STRING
            if properties is not None:
                updates.append("properties = @properties")
                params["properties"] = json.dumps(properties)
                param_types_dict["properties"] = param_types.JSON
            
            if not updates: return
            
            updates.append("updated_at = @updated_at")
            params["updated_at"] = spanner.COMMIT_TIMESTAMP
            param_types_dict["updated_at"] = param_types.TIMESTAMP
            
            sql = f"UPDATE DataSubjectTypes SET {', '.join(updates)} WHERE subject_id = @subject_id"
            transaction.execute_update(sql, params=params, param_types=param_types_dict)
        
        try:
            self.database.run_in_transaction(update_subject_txn)
            return True
        except Exception as e:
            print(f"Error updating data subject type: {e}")
            return False

    def delete_data_subject_type(self, subject_id: str) -> bool:
        """Delete a data subject type and its relationships."""
        def delete_subject_txn(transaction):
            transaction.execute_update(
                "DELETE FROM EntityRelationships WHERE source_id = @subject_id OR target_id = @subject_id",
                params={"subject_id": subject_id}, param_types={"subject_id": param_types.STRING}
            )
            transaction.execute_update(
                "DELETE FROM DataSubjectTypes WHERE subject_id = @subject_id",
                params={"subject_id": subject_id}, param_types={"subject_id": param_types.STRING}
            )
        try:
            self.database.run_in_transaction(delete_subject_txn)
            return True
        except Exception as e:
            print(f"Error deleting data subject type: {e}")
            return False

    def list_data_subject_types(self, limit: int = 100) -> list:
        """List all data subject types."""
        with self.database.snapshot() as snapshot:
            sql = "SELECT subject_id, name, description, properties, created_at, updated_at FROM DataSubjectTypes ORDER BY name LIMIT @limit"
            results = snapshot.execute_sql(sql, params={"limit": limit}, param_types={"limit": param_types.INT64})
            return [{
                "subject_id": row[0], "name": row[1], "description": row[2], "properties": row[3],
                "created_at": row[4].isoformat() if row[4] else None, "updated_at": row[5].isoformat() if row[5] else None
            } for row in results]

    # ===== CRUD OPERATIONS FOR VENDORS =====
    
    def create_vendor(self, name: str, description: str = None, properties: dict = None) -> str:
        """Create a new vendor, generate its embedding, and return its ID."""
        vendor_id = str(uuid.uuid4())
        properties_json = json.dumps(properties) if properties else None
        embedding = self._generate_embedding(name, description)
        
        def insert_vendor(transaction):
            transaction.insert(
                table="Vendors",
                columns=("vendor_id", "name", "description", "properties", "embedding", "created_at", "updated_at"),
                values=[(vendor_id, name, description, properties_json, embedding, spanner.COMMIT_TIMESTAMP, spanner.COMMIT_TIMESTAMP)]
            )
        
        try:
            self.database.run_in_transaction(insert_vendor)
            return vendor_id
        except Exception as e:
            print(f"Error creating vendor: {e}")
            return ""

    def get_vendor(self, vendor_id: str) -> dict:
        """Retrieve a vendor by ID."""
        with self.database.snapshot() as snapshot:
            sql = "SELECT vendor_id, name, description, properties, created_at, updated_at FROM Vendors WHERE vendor_id = @vendor_id"
            results = list(snapshot.execute_sql(sql, params={"vendor_id": vendor_id}, param_types={"vendor_id": param_types.STRING}))
            if not results: return None
            row = results[0]
            return {
                "vendor_id": row[0], "name": row[1], "description": row[2], "properties": row[3],
                "created_at": row[4].isoformat() if row[4] else None, "updated_at": row[5].isoformat() if row[5] else None
            }

    def update_vendor(self, vendor_id: str, name: str = None, description: str = None, properties: dict = None) -> bool:
        """Update a vendor. Re-calculates embedding if name or description changes."""
        def update_vendor_txn(transaction):
            updates = []
            params = {"vendor_id": vendor_id}
            param_types_dict = {"vendor_id": param_types.STRING}
            
            if name is not None or description is not None:
                read_sql = "SELECT name, description FROM Vendors WHERE vendor_id = @vendor_id"
                current_values = list(transaction.execute_sql(read_sql, params=params, param_types=param_types_dict))
                if not current_values: return
                
                current_name, current_desc = current_values[0]
                final_name = name if name is not None else current_name
                final_desc = description if description is not None else current_desc
                new_embedding = self._generate_embedding(final_name, final_desc)

                updates.append("embedding = @embedding")
                params["embedding"] = new_embedding
                param_types_dict["embedding"] = param_types.Array(param_types.FLOAT64)

            if name is not None:
                updates.append("name = @name")
                params["name"] = name
                param_types_dict["name"] = param_types.STRING
            if description is not None:
                updates.append("description = @description")
                params["description"] = description
                param_types_dict["description"] = param_types.STRING
            if properties is not None:
                updates.append("properties = @properties")
                params["properties"] = json.dumps(properties)
                param_types_dict["properties"] = param_types.JSON
            
            if not updates: return
            
            updates.append("updated_at = @updated_at")
            params["updated_at"] = spanner.COMMIT_TIMESTAMP
            param_types_dict["updated_at"] = param_types.TIMESTAMP
            
            sql = f"UPDATE Vendors SET {', '.join(updates)} WHERE vendor_id = @vendor_id"
            transaction.execute_update(sql, params=params, param_types=param_types_dict)
        
        try:
            self.database.run_in_transaction(update_vendor_txn)
            return True
        except Exception as e:
            print(f"Error updating vendor: {e}")
            return False

    def delete_vendor(self, vendor_id: str) -> bool:
        """Delete a vendor and its relationships."""
        def delete_vendor_txn(transaction):
            transaction.execute_update(
                "DELETE FROM EntityRelationships WHERE source_id = @vendor_id OR target_id = @vendor_id",
                params={"vendor_id": vendor_id}, param_types={"vendor_id": param_types.STRING}
            )
            transaction.execute_update(
                "DELETE FROM Vendors WHERE vendor_id = @vendor_id",
                params={"vendor_id": vendor_id}, param_types={"vendor_id": param_types.STRING}
            )
        try:
            self.database.run_in_transaction(delete_vendor_txn)
            return True
        except Exception as e:
            print(f"Error deleting vendor: {e}")
            return False

    def list_vendors(self, limit: int = 100) -> list:
        """List all vendors."""
        with self.database.snapshot() as snapshot:
            sql = "SELECT vendor_id, name, description, properties, created_at, updated_at FROM Vendors ORDER BY name LIMIT @limit"
            results = snapshot.execute_sql(sql, params={"limit": limit}, param_types={"limit": param_types.INT64})
            return [{
                "vendor_id": row[0], "name": row[1], "description": row[2], "properties": row[3],
                "created_at": row[4].isoformat() if row[4] else None, "updated_at": row[5].isoformat() if row[5] else None
            } for row in results]

    # ===== CRUD OPERATIONS FOR RELATIONSHIPS =====
    
    def create_relationship(self, source_id: str, target_id: str, relationship_type: str, properties: dict = None) -> bool:
        """Create a new relationship between entities. Returns True if successful."""
        properties_json = json.dumps(properties) if properties else None
        
        def insert_relationship(transaction):
            transaction.insert(
                table="EntityRelationships",
                columns=("source_id", "target_id", "relationship_type", "properties", "created_at", "updated_at"),
                values=[(source_id, target_id, relationship_type, properties_json, spanner.COMMIT_TIMESTAMP, spanner.COMMIT_TIMESTAMP)]
            )
        
        try:
            self.database.run_in_transaction(insert_relationship)
            return True
        except Exception as e:
            print(f"Error creating relationship: {e}")
            return False

    def get_relationships(self, entity_id: str = None, relationship_type: str = None, limit: int = 100) -> list:
        """Get relationships. Can filter by entity_id or relationship_type."""
        with self.database.snapshot() as snapshot:
            where_clauses = []
            params = {"limit": limit}
            param_types_dict = {"limit": param_types.INT64}
            
            if entity_id:
                where_clauses.append("(source_id = @entity_id OR target_id = @entity_id)")
                params["entity_id"] = entity_id
                param_types_dict["entity_id"] = param_types.STRING
            
            if relationship_type:
                where_clauses.append("relationship_type = @relationship_type")
                params["relationship_type"] = relationship_type
                param_types_dict["relationship_type"] = param_types.STRING
            
            where_clause = " WHERE " + " AND ".join(where_clauses) if where_clauses else ""
            sql = f"SELECT source_id, target_id, relationship_type, properties, created_at, updated_at FROM EntityRelationships{where_clause} LIMIT @limit"
            
            results = snapshot.execute_sql(sql, params=params, param_types=param_types_dict)
            return [{
                "source_id": row[0], "target_id": row[1], "relationship_type": row[2], "properties": row[3],
                "created_at": row[4].isoformat() if row[4] else None, "updated_at": row[5].isoformat() if row[5] else None
            } for row in results]

    def update_relationship(self, source_id: str, target_id: str, relationship_type: str = None, properties: dict = None) -> bool:
        """Update a relationship. Returns True if successful."""
        def update_relationship_txn(transaction):
            updates = []
            params = {"source_id": source_id, "target_id": target_id}
            param_types_dict = {"source_id": param_types.STRING, "target_id": param_types.STRING}
            
            if relationship_type is not None:
                updates.append("relationship_type = @relationship_type")
                params["relationship_type"] = relationship_type
                param_types_dict["relationship_type"] = param_types.STRING
            if properties is not None:
                updates.append("properties = @properties")
                params["properties"] = json.dumps(properties)
                param_types_dict["properties"] = param_types.JSON
            
            if not updates: return
            
            updates.append("updated_at = @updated_at")
            params["updated_at"] = spanner.COMMIT_TIMESTAMP
            param_types_dict["updated_at"] = param_types.TIMESTAMP
            
            sql = f"UPDATE EntityRelationships SET {', '.join(updates)} WHERE source_id = @source_id AND target_id = @target_id"
            transaction.execute_update(sql, params=params, param_types=param_types_dict)
        
        try:
            self.database.run_in_transaction(update_relationship_txn)
            return True
        except Exception as e:
            print(f"Error updating relationship: {e}")
            return False

    def delete_relationship(self, source_id: str, target_id: str) -> bool:
        """Delete a specific relationship. Returns True if successful."""
        def delete_relationship_txn(transaction):
            transaction.execute_update(
                "DELETE FROM EntityRelationships WHERE source_id = @source_id AND target_id = @target_id",
                params={"source_id": source_id, "target_id": target_id},
                param_types={"source_id": param_types.STRING, "target_id": param_types.STRING}
            )
        
        try:
            self.database.run_in_transaction(delete_relationship_txn)
            return True
        except Exception as e:
            print(f"Error deleting relationship: {e}")
            return False

    def list_all_relationships(self, limit: int = 1000, with_entity_details: bool = False) -> list:
        """List all relationships in the database with optional entity details."""
        try:
            # First snapshot: Get all relationships
            relationships = []
            entity_ids = set()
            
            with self.database.snapshot() as snapshot1:
                sql = "SELECT source_id, target_id, relationship_type, properties, created_at, updated_at FROM EntityRelationships LIMIT @limit"
                results = snapshot1.execute_sql(sql, params={"limit": limit}, param_types={"limit": param_types.INT64})
                
                for row in results:
                    source_id, target_id = row[0], row[1]
                    relationships.append({
                        "source_id": source_id, "target_id": target_id, "relationship_type": row[2],
                        "properties": row[3], "created_at": row[4].isoformat() if row[4] else None,
                        "updated_at": row[5].isoformat() if row[5] else None
                    })
                    if with_entity_details:
                        entity_ids.add(source_id)
                        entity_ids.add(target_id)
            
            # Second snapshot: Get entity details if needed
            if with_entity_details and entity_ids:
                entity_details = {}
                with self.database.snapshot() as entity_snapshot:
                    entity_tables = {
                        "Assets": "asset_id", "ProcessingActivities": "activity_id", "DataElements": "element_id",
                        "DataSubjectTypes": "subject_id", "Vendors": "vendor_id"
                    }
                    entity_id_list = list(entity_ids)
                    for table, id_column in entity_tables.items():
                        sql = f"SELECT {id_column}, name, properties FROM {table} WHERE {id_column} IN UNNEST(@entity_ids)"
                        params = {"entity_ids": entity_id_list}
                        param_types_dict = {"entity_ids": param_types.Array(param_types.STRING)}
                        results = entity_snapshot.execute_sql(sql, params=params, param_types=param_types_dict)
                        for row in results:
                            entity_details[row[0]] = {"name": row[1], "type": table[:-1], "properties": row[2]}
                
                for relationship in relationships:
                    source_details = entity_details.get(relationship["source_id"], {})
                    target_details = entity_details.get(relationship["target_id"], {})
                    relationship["source_name"] = source_details.get("name", "Unknown")
                    relationship["source_type"] = source_details.get("type", "Unknown")
                    relationship["target_name"] = target_details.get("name", "Unknown")
                    relationship["target_type"] = target_details.get("type", "Unknown")
            
            return relationships
        except Exception as e:
            print(f"Error listing relationships: {e}")
            return []
            
    # ===== METADATA METHODS =====
    
    def get_entity_types(self) -> list:
        """Get all available entity types in the system.
        
        Returns:
            A list of entity type dictionaries with name and description.
        """
        try:
            entity_types = []
            
            # Query the EntityTypes table to get all entity types
            with self.database.snapshot() as snapshot:
                sql = "SELECT name, description, table_name, id_column FROM EntityTypes ORDER BY name"
                results = snapshot.execute_sql(sql)
                
                for row in results:
                    entity_types.append({
                        "name": row[0],
                        "description": row[1],
                        "table_name": row[2],
                        "id_column": row[3]
                    })
            
            return entity_types
        except Exception as e:
            print(f"Error getting entity types: {e}")
            return []
    
    def get_entity_parameters(self, entity_type: str) -> list:
        """Get the parameters (fields) for a specific entity type.
        
        Args:
            entity_type: The type of entity to get parameters for
            
        Returns:
            A list of parameter dictionaries with name, description, and required flag.
        """
        try:
            parameters = []
            
            # First, get the type_id for the requested entity type
            type_id = None
            with self.database.snapshot() as snapshot:
                sql = "SELECT type_id FROM EntityTypes WHERE name = @entity_type"
                params = {"entity_type": entity_type}
                param_types_dict = {"entity_type": param_types.STRING}
                results = snapshot.execute_sql(sql, params=params, param_types=param_types_dict)
                
                for row in results:
                    type_id = row[0]
                    break
            
            # If we found the type_id, query for its properties
            if type_id:
                with self.database.snapshot() as snapshot:
                    sql = """SELECT property_name, description, data_type, is_required 
                             FROM EntityTypeProperties 
                             WHERE type_id = @type_id 
                             ORDER BY is_required DESC, property_name"""
                    params = {"type_id": type_id}
                    param_types_dict = {"type_id": param_types.STRING}
                    results = snapshot.execute_sql(sql, params=params, param_types=param_types_dict)
                    
                    for row in results:
                        parameters.append({
                            "name": row[0],
                            "description": row[1],
                            "data_type": row[2],
                            "required": row[3]
                        })
            
            return parameters
        except Exception as e:
            print(f"Error getting entity parameters: {e}")
            return []
    
    def get_relationship_ontology(self) -> list:
        """Get the relationship ontology defining valid relationships between entity types.
        
        Returns:
            A list of relationship dictionaries with source_type, target_type, relationship_type, and description.
        """
        try:
            ontology = []
            
            # Query the RelationshipOntology table to get all defined relationships
            with self.database.snapshot() as snapshot:
                sql = """
                SELECT 
                    s.name as source_type, 
                    t.name as target_type, 
                    ro.relationship_type, 
                    ro.description
                FROM 
                    RelationshipOntology ro
                JOIN 
                    EntityTypes s ON ro.source_type_id = s.type_id
                JOIN 
                    EntityTypes t ON ro.target_type_id = t.type_id
                ORDER BY 
                    s.name, t.name, ro.relationship_type
                """
                results = snapshot.execute_sql(sql)
                
                for row in results:
                    ontology.append({
                        "source_type": row[0],
                        "target_type": row[1],
                        "relationship_type": row[2],
                        "description": row[3]
                    })
            
            return ontology
        except Exception as e:
            print(f"Error getting relationship ontology: {e}")
            return []