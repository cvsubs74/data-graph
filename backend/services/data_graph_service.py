import os
import json
import uuid

import vertexai
from vertexai.generative_models import GenerativeModel

from google.cloud import spanner, secretmanager
from google.cloud.spanner_v1 import param_types

class DataGraphService:
    """A service class to manage all interactions with the data graph.

    This includes initializing GCP clients, ingesting documents, and answering
    questions by querying the Spanner database and using Vertex AI models.
    """

    def __init__(self):
        """Initializes all necessary GCP clients and configurations."""
        try:
            self.project_id = os.environ.get("GCP_PROJECT")
            if not self.project_id:
                raise ValueError("GCP_PROJECT environment variable not set.")

            vertexai.init(project=self.project_id, location="us-central1")
            self.llm_model = GenerativeModel("gemini-2.5-flash-lite")

            secret_client = secretmanager.SecretManagerServiceClient()
            
            def get_secret(secret_id):
                name = f"projects/{self.project_id}/secrets/{secret_id}/versions/latest"
                response = secret_client.access_secret_version(request={"name": name})
                return response.payload.data.decode("UTF-8")

            spanner_instance_id = get_secret("spanner-instance-id")
            spanner_database_id = get_secret("spanner-database-id")

            spanner_client = spanner.Client(project=self.project_id)
            instance = spanner_client.instance(spanner_instance_id)
            self.database = instance.database(spanner_database_id)
            print("DataGraphService initialized successfully.")

        except Exception as e:
            print(f"FATAL: Could not initialize DataGraphService: {e}")
            self.llm_model = None
            self.database = None

    def ingest_document(self, document_text: str) -> dict:
        """Extracts a graph from text and populates Spanner."""
        graph_data = self._extract_graph_from_document(document_text)
        if not graph_data or not graph_data.get("nodes"):
            raise ValueError("Failed to extract a valid graph from the document.")
        
        self._populate_spanner_from_data(graph_data)
        return {
            'nodes_found': len(graph_data.get('nodes', [])),
            'relationships_found': len(graph_data.get('relationships', []))
        }



    def is_initialized(self) -> bool:
        """Check if the service is properly initialized."""
        return self.database is not None and self.llm_model is not None

    # ===== CRUD OPERATIONS FOR ASSETS =====
    
    def create_asset(self, name: str, description: str = None, properties: dict = None) -> str:
        """Create a new asset and return its ID."""
        asset_id = str(uuid.uuid4())
        
        # Convert properties dict to JSON string if it exists
        properties_json = json.dumps(properties) if properties else None
        
        def insert_asset(transaction):
            transaction.insert(
                table="Assets",
                columns=("asset_id", "name", "description", "properties", "created_at", "updated_at"),
                values=[(asset_id, name, description, properties_json, spanner.COMMIT_TIMESTAMP, spanner.COMMIT_TIMESTAMP)]
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
        """Update an asset. Returns True if successful."""
        def update_asset_txn(transaction):
            # Build dynamic update query
            updates = []
            params = {"asset_id": asset_id}
            param_types_dict = {"asset_id": param_types.STRING}
            
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
                params["properties"] = properties
                param_types_dict["properties"] = param_types.JSON
            
            if not updates:
                return
            
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
            # Delete relationships first
            transaction.execute_update(
                "DELETE FROM EntityRelationships WHERE source_id = @asset_id OR target_id = @asset_id",
                params={"asset_id": asset_id},
                param_types={"asset_id": param_types.STRING}
            )
            # Delete the asset
            transaction.execute_update(
                "DELETE FROM Assets WHERE asset_id = @asset_id",
                params={"asset_id": asset_id},
                param_types={"asset_id": param_types.STRING}
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
            
            assets = []
            for row in results:
                assets.append({
                    "asset_id": row[0],
                    "name": row[1],
                    "description": row[2],
                    "properties": row[3],
                    "created_at": row[4].isoformat() if row[4] else None,
                    "updated_at": row[5].isoformat() if row[5] else None
                })
            return assets

    # ===== CRUD OPERATIONS FOR PROCESSING ACTIVITIES =====
    
    def create_processing_activity(self, name: str, description: str = None, properties: dict = None) -> str:
        """Create a new processing activity and return its ID."""
        activity_id = str(uuid.uuid4())
        
        # Convert properties dict to JSON string if it exists
        properties_json = json.dumps(properties) if properties else None
        
        def insert_activity(transaction):
            transaction.insert(
                table="ProcessingActivities",
                columns=("activity_id", "name", "description", "properties", "created_at", "updated_at"),
                values=[(activity_id, name, description, properties_json, spanner.COMMIT_TIMESTAMP, spanner.COMMIT_TIMESTAMP)]
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
            
            if not results:
                return None
            
            row = results[0]
            return {
                "activity_id": row[0],
                "name": row[1],
                "description": row[2],
                "properties": row[3],
                "created_at": row[4].isoformat() if row[4] else None,
                "updated_at": row[5].isoformat() if row[5] else None
            }

    def update_processing_activity(self, activity_id: str, name: str = None, description: str = None, properties: dict = None) -> bool:
        """Update a processing activity. Returns True if successful."""
        def update_activity_txn(transaction):
            updates = []
            params = {"activity_id": activity_id}
            param_types_dict = {"activity_id": param_types.STRING}
            
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
                params["properties"] = properties
                param_types_dict["properties"] = param_types.JSON
            
            if not updates:
                return
            
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
        """Delete a processing activity and its relationships. Returns True if successful."""
        def delete_activity_txn(transaction):
            transaction.execute_update(
                "DELETE FROM EntityRelationships WHERE source_id = @activity_id OR target_id = @activity_id",
                params={"activity_id": activity_id},
                param_types={"activity_id": param_types.STRING}
            )
            transaction.execute_update(
                "DELETE FROM ProcessingActivities WHERE activity_id = @activity_id",
                params={"activity_id": activity_id},
                param_types={"activity_id": param_types.STRING}
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
            
            activities = []
            for row in results:
                activities.append({
                    "activity_id": row[0],
                    "name": row[1],
                    "description": row[2],
                    "properties": row[3],
                    "created_at": row[4].isoformat() if row[4] else None,
                    "updated_at": row[5].isoformat() if row[5] else None
                })
            return activities

    # ===== CRUD OPERATIONS FOR DATA ELEMENTS =====
    
    def create_data_element(self, name: str, description: str = None, properties: dict = None) -> str:
        """Create a new data element and return its ID."""
        element_id = str(uuid.uuid4())
        
        # Convert properties dict to JSON string if it exists
        properties_json = json.dumps(properties) if properties else None
        
        def insert_element(transaction):
            transaction.insert(
                table="DataElements",
                columns=("element_id", "name", "description", "properties", "created_at", "updated_at"),
                values=[(element_id, name, description, properties_json, spanner.COMMIT_TIMESTAMP, spanner.COMMIT_TIMESTAMP)]
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
            
            if not results:
                return None
            
            row = results[0]
            return {
                "element_id": row[0],
                "name": row[1],
                "description": row[2],
                "properties": row[3],
                "created_at": row[4].isoformat() if row[4] else None,
                "updated_at": row[5].isoformat() if row[5] else None
            }

    def update_data_element(self, element_id: str, name: str = None, description: str = None, properties: dict = None) -> bool:
        """Update a data element. Returns True if successful."""
        def update_element_txn(transaction):
            updates = []
            params = {"element_id": element_id}
            param_types_dict = {"element_id": param_types.STRING}
            
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
                params["properties"] = properties
                param_types_dict["properties"] = param_types.JSON
            
            if not updates:
                return
            
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
        """Delete a data element and its relationships. Returns True if successful."""
        def delete_element_txn(transaction):
            transaction.execute_update(
                "DELETE FROM EntityRelationships WHERE source_id = @element_id OR target_id = @element_id",
                params={"element_id": element_id},
                param_types={"element_id": param_types.STRING}
            )
            transaction.execute_update(
                "DELETE FROM DataElements WHERE element_id = @element_id",
                params={"element_id": element_id},
                param_types={"element_id": param_types.STRING}
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
            
            elements = []
            for row in results:
                elements.append({
                    "element_id": row[0],
                    "name": row[1],
                    "description": row[2],
                    "properties": row[3],
                    "created_at": row[4].isoformat() if row[4] else None,
                    "updated_at": row[5].isoformat() if row[5] else None
                })
            return elements

    # ===== CRUD OPERATIONS FOR DATA SUBJECT TYPES =====
    
    def create_data_subject_type(self, name: str, description: str = None, properties: dict = None) -> str:
        """Create a new data subject type and return its ID."""
        subject_id = str(uuid.uuid4())
        
        def insert_subject(transaction):
            transaction.insert(
                table="DataSubjectTypes",
                columns=("subject_id", "name", "description", "properties", "created_at", "updated_at"),
                values=[(subject_id, name, description, properties, spanner.COMMIT_TIMESTAMP, spanner.COMMIT_TIMESTAMP)]
            )
        
        self.database.run_in_transaction(insert_subject)
        return subject_id

    def get_data_subject_type(self, subject_id: str) -> dict:
        """Retrieve a data subject type by ID."""
        with self.database.snapshot() as snapshot:
            sql = "SELECT subject_id, name, description, properties, created_at, updated_at FROM DataSubjectTypes WHERE subject_id = @subject_id"
            results = list(snapshot.execute_sql(sql, params={"subject_id": subject_id}, param_types={"subject_id": param_types.STRING}))
            
            if not results:
                return None
            
            row = results[0]
            return {
                "subject_id": row[0],
                "name": row[1],
                "description": row[2],
                "properties": row[3],
                "created_at": row[4].isoformat() if row[4] else None,
                "updated_at": row[5].isoformat() if row[5] else None
            }

    def update_data_subject_type(self, subject_id: str, name: str = None, description: str = None, properties: dict = None) -> bool:
        """Update a data subject type. Returns True if successful."""
        def update_subject_txn(transaction):
            updates = []
            params = {"subject_id": subject_id}
            param_types_dict = {"subject_id": param_types.STRING}
            
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
                params["properties"] = properties
                param_types_dict["properties"] = param_types.JSON
            
            if not updates:
                return
            
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
        """Delete a data subject type and its relationships. Returns True if successful."""
        def delete_subject_txn(transaction):
            transaction.execute_update(
                "DELETE FROM EntityRelationships WHERE source_id = @subject_id OR target_id = @subject_id",
                params={"subject_id": subject_id},
                param_types={"subject_id": param_types.STRING}
            )
            transaction.execute_update(
                "DELETE FROM DataSubjectTypes WHERE subject_id = @subject_id",
                params={"subject_id": subject_id},
                param_types={"subject_id": param_types.STRING}
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
            
            subjects = []
            for row in results:
                subjects.append({
                    "subject_id": row[0],
                    "name": row[1],
                    "description": row[2],
                    "properties": row[3],
                    "created_at": row[4].isoformat() if row[4] else None,
                    "updated_at": row[5].isoformat() if row[5] else None
                })
            return subjects

    # ===== CRUD OPERATIONS FOR VENDORS =====
    
    def create_vendor(self, name: str, description: str = None, properties: dict = None) -> str:
        """Create a new vendor and return its ID."""
        vendor_id = str(uuid.uuid4())
        
        def insert_vendor(transaction):
            transaction.insert(
                table="Vendors",
                columns=("vendor_id", "name", "description", "properties", "created_at", "updated_at"),
                values=[(vendor_id, name, description, properties, spanner.COMMIT_TIMESTAMP, spanner.COMMIT_TIMESTAMP)]
            )
        
        self.database.run_in_transaction(insert_vendor)
        return vendor_id

    def get_vendor(self, vendor_id: str) -> dict:
        """Retrieve a vendor by ID."""
        with self.database.snapshot() as snapshot:
            sql = "SELECT vendor_id, name, description, properties, created_at, updated_at FROM Vendors WHERE vendor_id = @vendor_id"
            results = list(snapshot.execute_sql(sql, params={"vendor_id": vendor_id}, param_types={"vendor_id": param_types.STRING}))
            
            if not results:
                return None
            
            row = results[0]
            return {
                "vendor_id": row[0],
                "name": row[1],
                "description": row[2],
                "properties": row[3],
                "created_at": row[4].isoformat() if row[4] else None,
                "updated_at": row[5].isoformat() if row[5] else None
            }

    def update_vendor(self, vendor_id: str, name: str = None, description: str = None, properties: dict = None) -> bool:
        """Update a vendor. Returns True if successful."""
        def update_vendor_txn(transaction):
            updates = []
            params = {"vendor_id": vendor_id}
            param_types_dict = {"vendor_id": param_types.STRING}
            
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
                params["properties"] = properties
                param_types_dict["properties"] = param_types.JSON
            
            if not updates:
                return
            
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
        """Delete a vendor and its relationships. Returns True if successful."""
        def delete_vendor_txn(transaction):
            transaction.execute_update(
                "DELETE FROM EntityRelationships WHERE source_id = @vendor_id OR target_id = @vendor_id",
                params={"vendor_id": vendor_id},
                param_types={"vendor_id": param_types.STRING}
            )
            transaction.execute_update(
                "DELETE FROM Vendors WHERE vendor_id = @vendor_id",
                params={"vendor_id": vendor_id},
                param_types={"vendor_id": param_types.STRING}
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
            
            vendors = []
            for row in results:
                vendors.append({
                    "vendor_id": row[0],
                    "name": row[1],
                    "description": row[2],
                    "properties": row[3],
                    "created_at": row[4].isoformat() if row[4] else None,
                    "updated_at": row[5].isoformat() if row[5] else None
                })
            return vendors

    # ===== CRUD OPERATIONS FOR RELATIONSHIPS =====
    
    def create_relationship(self, source_id: str, target_id: str, relationship_type: str, properties: dict = None) -> bool:
        """Create a new relationship between entities. Returns True if successful."""
        # Convert properties dict to JSON string if it exists
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
            
            relationships = []
            for row in results:
                relationships.append({
                    "source_id": row[0],
                    "target_id": row[1],
                    "relationship_type": row[2],
                    "properties": row[3],
                    "created_at": row[4].isoformat() if row[4] else None,
                    "updated_at": row[5].isoformat() if row[5] else None
                })
            return relationships

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
                params["properties"] = properties
                param_types_dict["properties"] = param_types.JSON
            
            if not updates:
                return
            
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

    def _extract_graph_from_document(self, document_text: str) -> dict:
        prompt = f"""You are an expert at building knowledge graphs for data governance and privacy regulations. Your task is to extract information from the provided document according to a specific schema.

**Schema & Topology Rules:**
1.  Identify and classify entities into one of five types:
    - **Asset**: A system, application, or database (e.g., 'CRM Platform', 'Production Aurora DB').
    - **ProcessingActivity**: A business process that uses data (e.g., 'User Authentication', 'Monthly Newsletter Campaign').
    - **DataElement**: A specific category of personal data (e.g., 'Contact Info', 'Financial Info', 'IP Address').
    - **DataSubjectType**: A category of individual (e.g., 'Customer', 'Employee', 'Patient').
    - **Vendor**: A third-party company or service.
2.  Identify the relationships between these entities. Common relationships include:
    - A 'ProcessingActivity' **PROCESSES_DATA_FROM** an 'Asset'.
    - An 'Asset' **CONTAINS** 'DataElements'.
    - A 'DataElement' **BELONGS_TO** a 'DataSubjectType'.
    - An 'Asset' **TRANSFERS_TO** a 'Vendor'.

**Output Format:**
- Return a single, valid JSON object with 'nodes' and 'relationships' keys. Do not include any other text.
- 'nodes' is a list of objects, each with 'id' (a unique name) and 'type'.
- 'relationships' is a list of objects, each with 'source' (name), 'target' (name), and 'relationship_type'.

**Document:**
---
{document_text}
---
    """
        try:
            response = self.llm_model.generate_content(prompt)
            cleaned_response = response.text.strip().replace("```json", "").replace("```", "").strip()
            return json.loads(cleaned_response)
        except (json.JSONDecodeError, AttributeError, ValueError) as e:
            print(f"Error parsing LLM response: {e}")
            return {"nodes": [], "relationships": []}

    def _populate_spanner_from_data(self, graph_data: dict):
        """Populate Spanner database using CRUD methods for better consistency and error handling."""
        name_to_uuid_map = {}
        created_entities = 0
        created_relationships = 0
        
        # Create entities using CRUD methods
        for node in graph_data.get('nodes', []):
            node_name = node['id']
            node_type = node.get('type')
            node_description = node.get('description')  # Extract description if provided
            node_properties = node.get('properties')    # Extract properties if provided
            
            try:
                # Use the appropriate CRUD method based on entity type
                if node_type == "Asset":
                    entity_uuid = self.create_asset(node_name, node_description, node_properties)
                elif node_type == "ProcessingActivity":
                    entity_uuid = self.create_processing_activity(node_name, node_description, node_properties)
                elif node_type == "DataElement":
                    entity_uuid = self.create_data_element(node_name, node_description, node_properties)
                elif node_type == "DataSubjectType":
                    entity_uuid = self.create_data_subject_type(node_name, node_description, node_properties)
                elif node_type == "Vendor":
                    entity_uuid = self.create_vendor(node_name, node_description, node_properties)
                else:
                    print(f"Warning: Unknown entity type '{node_type}' for node '{node_name}'. Skipping.")
                    continue
                
                name_to_uuid_map[node_name] = entity_uuid
                created_entities += 1
                
            except Exception as e:
                print(f"Error creating {node_type} '{node_name}': {e}")
                continue

        # Create relationships using CRUD methods
        for rel in graph_data.get('relationships', []):
            source_name = rel.get('source')
            target_name = rel.get('target')
            relationship_type = rel.get('relationship_type')
            relationship_properties = rel.get('properties')  # Extract properties if provided
            
            source_uuid = name_to_uuid_map.get(source_name)
            target_uuid = name_to_uuid_map.get(target_name)
            
            if not source_uuid or not target_uuid:
                print(f"Warning: Skipping relationship '{relationship_type}' between '{source_name}' and '{target_name}' - one or both entities not found.")
                continue
            
            try:
                success = self.create_relationship(source_uuid, target_uuid, relationship_type, relationship_properties)
                if success:
                    created_relationships += 1
                else:
                    print(f"Failed to create relationship '{relationship_type}' between '{source_name}' and '{target_name}'")
                    
            except Exception as e:
                print(f"Error creating relationship '{relationship_type}' between '{source_name}' and '{target_name}': {e}")
                continue

        print(f"Successfully created {created_entities} entities and {created_relationships} relationships using CRUD methods.")

    def _get_all_entity_names(self, snapshot) -> dict:
        entity_tables = {
            "Assets": "asset_id", "ProcessingActivities": "activity_id", "DataElements": "element_id",
            "DataSubjectTypes": "subject_id", "Vendors": "vendor_id"
        }
        name_to_id_map = {}
        for table, id_column in entity_tables.items():
            sql = f"SELECT {id_column}, name FROM {table}"
            results = snapshot.execute_sql(sql)
            for row in results:
                name_to_id_map[row[1]] = row[0]
        return name_to_id_map

    def _get_entity_details_direct(self, transaction, entity_ids: list) -> dict:
        if not entity_ids:
            return {}
        entity_tables = {
            "Assets": "asset_id", "ProcessingActivities": "activity_id", "DataElements": "element_id",
            "DataSubjectTypes": "subject_id", "Vendors": "vendor_id"
        }
        fetched_details = {}
        for table, id_column in entity_tables.items():
            sql = f"SELECT {id_column}, name, properties FROM {table} WHERE {id_column} IN UNNEST(@entity_ids)"
            params = {"entity_ids": entity_ids}
            param_types_dict = {"entity_ids": param_types.Array(param_types.STRING)}
            results = transaction.execute_sql(sql, params=params, param_types=param_types_dict)
            for row in results:
                fetched_details[row[0]] = {"name": row[1], "type": table[:-1], "properties": row[2]}
        return fetched_details

    def list_all_relationships(self, limit: int = 1000, with_entity_details: bool = False) -> list:
        """List all relationships in the database with optional entity details.
        
        Args:
            limit: Maximum number of relationships to return
            with_entity_details: If True, include entity details (name, type) for source and target
            
        Returns:
            List of relationship dictionaries
        """
        try:
            # First, get all relationships
            relationships = []
            entity_ids = set()
            
            with self.database.snapshot() as snapshot:
                sql = "SELECT source_id, target_id, relationship_type, properties, created_at, updated_at FROM EntityRelationships LIMIT @limit"
                results = snapshot.execute_sql(sql, params={"limit": limit}, param_types={"limit": param_types.INT64})
                
                # Collect all relationships and entity IDs
                for row in results:
                    source_id = row[0]
                    target_id = row[1]
                    
                    relationship = {
                        "source_id": source_id,
                        "target_id": target_id,
                        "relationship_type": row[2],
                        "properties": row[3],
                        "created_at": row[4].isoformat() if row[4] else None,
                        "updated_at": row[5].isoformat() if row[5] else None
                    }
                    
                    relationships.append(relationship)
                    
                    if with_entity_details:
                        entity_ids.add(source_id)
                        entity_ids.add(target_id)
            
            # If entity details are requested, fetch them in a separate snapshot
            if with_entity_details and entity_ids:
                entity_details = {}
                
                # Create a new snapshot for entity details
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
                
                # Add entity details to relationships
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


