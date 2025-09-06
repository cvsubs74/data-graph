import os
import json
import uuid
import numpy as np
import requests
from typing import List, Dict, Any, Optional

import vertexai
from vertexai.generative_models import GenerativeModel
from vertexai.preview.language_models import TextEmbeddingModel

from google.cloud import spanner, secretmanager
from google.cloud.spanner_v1 import param_types

class VendorRiskService:
    """A service class to manage all interactions with the vendor risk analysis system.

    This includes initializing GCP clients, retrieving risk questions, and managing
    vendor risk assessments using Vertex AI models.
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
            
            print(f"Initializing VendorRiskService with project ID: {self.project_id}")
            
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
                
            print("VendorRiskService initialization completed successfully.")

        except Exception as e:
            print(f"FATAL: Could not initialize VendorRiskService: {e}")
            # Ensure all components are set to None if initialization fails
            self.database = None
            self.embedding_model = None

    def is_initialized(self) -> bool:
        """Check if the service is properly initialized."""
        return self.database is not None and self.embedding_model is not None

    # ===== RISK QUESTIONS MANAGEMENT =====

    def get_risk_questions(self) -> List[Dict[str, Any]]:
        """
        Retrieves all risk assessment questions.
        
        Returns:
            A list of question dictionaries with question_id, question_text, question_type, etc.
        """
        questions = []
        
        try:
            # Use context manager for the main query
            with self.database.snapshot() as snapshot:
                sql = """
                    SELECT question_id, question_text, question_type, category, is_required
                    FROM RiskQuestions
                    ORDER BY category, question_id
                """
                results = list(snapshot.execute_sql(sql))
            
            for row in results:
                question = {
                    "question_id": row[0],
                    "question_text": row[1],
                    "question_type": row[2],
                    "category": row[3],
                    "is_required": row[4]
                }
                
                # If question type is single_select, get the options
                if row[2] == "single_select":
                    # Use context manager for options query
                    with self.database.snapshot() as options_snapshot:
                        options_sql = """
                            SELECT option_id, option_text
                            FROM QuestionOptions
                            WHERE question_id = @question_id
                            ORDER BY option_id
                        """
                        options_params = {"question_id": row[0]}
                        options_param_types = {"question_id": param_types.STRING}
                        
                        options_results = list(options_snapshot.execute_sql(
                            options_sql, 
                            params=options_params, 
                            param_types=options_param_types
                        ))
                    
                    options = []
                    for option_row in options_results:
                        options.append({
                            "option_id": option_row[0],
                            "option_text": option_row[1]
                        })
                    
                    question["options"] = options
                
                questions.append(question)
                
            return questions
        except Exception as e:
            print(f"Error getting risk questions: {e}")
            return []

    def create_risk_question(self, question_text: str, question_type: str, category: str, 
                           is_required: bool = True, options: List[Dict[str, str]] = None) -> str:
        """
        Creates a new risk assessment question.
        
        Args:
            question_text: The text of the question
            question_type: The type of question (yes_no, free_text, single_select)
            category: The category the question belongs to
            is_required: Whether the question is required
            options: List of option dictionaries for single_select questions
            
        Returns:
            The unique question_id of the created question
        """
        question_id = str(uuid.uuid4())
        
        def insert_question(transaction):
            # Insert the question
            transaction.insert(
                table="RiskQuestions",
                columns=("question_id", "question_text", "question_type", "category", "is_required", "created_at", "updated_at"),
                values=[(
                    question_id, question_text, question_type, category, 
                    is_required, spanner.COMMIT_TIMESTAMP, spanner.COMMIT_TIMESTAMP
                )]
            )
            
            # If it's a single_select question, insert the options
            if question_type == "single_select" and options:
                option_values = []
                for option in options:
                    option_id = str(uuid.uuid4())
                    option_text = option.get("option_text", "")
                    option_values.append((
                        option_id, question_id, option_text, 
                        spanner.COMMIT_TIMESTAMP, spanner.COMMIT_TIMESTAMP
                    ))
                
                if option_values:
                    transaction.insert(
                        table="QuestionOptions",
                        columns=("option_id", "question_id", "option_text", "created_at", "updated_at"),
                        values=option_values
                    )
        
        try:
            self.database.run_in_transaction(insert_question)
            return question_id
        except Exception as e:
            print(f"Error creating risk question: {e}")
            return ""

    def update_risk_question(self, question_id: str, question_text: str = None, 
                           question_type: str = None, category: str = None,
                           is_required: bool = None, options: List[Dict[str, str]] = None) -> bool:
        """
        Updates an existing risk assessment question.
        
        Args:
            question_id: The unique identifier of the question to update
            question_text: Optional new text for the question
            question_type: Optional new type for the question
            category: Optional new category for the question
            is_required: Optional new required flag for the question
            options: Optional new options for single_select questions
            
        Returns:
            True if the update was successful, False otherwise
        """
        def update_question_txn(transaction):
            # Update the question
            updates = []
            params = {"question_id": question_id}
            param_types_dict = {"question_id": param_types.STRING}
            
            if question_text is not None:
                updates.append("question_text = @question_text")
                params["question_text"] = question_text
                param_types_dict["question_text"] = param_types.STRING
                
            if question_type is not None:
                updates.append("question_type = @question_type")
                params["question_type"] = question_type
                param_types_dict["question_type"] = param_types.STRING
                
            if category is not None:
                updates.append("category = @category")
                params["category"] = category
                param_types_dict["category"] = param_types.STRING
                
            if is_required is not None:
                updates.append("is_required = @is_required")
                params["is_required"] = is_required
                param_types_dict["is_required"] = param_types.BOOL
            
            if updates:
                updates.append("updated_at = @updated_at")
                params["updated_at"] = spanner.COMMIT_TIMESTAMP
                param_types_dict["updated_at"] = param_types.TIMESTAMP
                
                sql = f"UPDATE RiskQuestions SET {', '.join(updates)} WHERE question_id = @question_id"
                transaction.execute_update(sql, params=params, param_types=param_types_dict)
            
            # If options are provided and the question type is or was single_select, update options
            if options is not None:
                # First, delete existing options
                transaction.execute_update(
                    "DELETE FROM QuestionOptions WHERE question_id = @question_id",
                    params={"question_id": question_id},
                    param_types={"question_id": param_types.STRING}
                )
                
                # Then insert new options
                option_values = []
                for option in options:
                    option_id = str(uuid.uuid4())
                    option_text = option.get("option_text", "")
                    option_values.append((
                        option_id, question_id, option_text, 
                        spanner.COMMIT_TIMESTAMP, spanner.COMMIT_TIMESTAMP
                    ))
                
                if option_values:
                    transaction.insert(
                        table="QuestionOptions",
                        columns=("option_id", "question_id", "option_text", "created_at", "updated_at"),
                        values=option_values
                    )
        
        try:
            self.database.run_in_transaction(update_question_txn)
            return True
        except Exception as e:
            print(f"Error updating risk question: {e}")
            return False

    def delete_risk_question(self, question_id: str) -> bool:
        """
        Deletes a risk assessment question and its options.
        
        Args:
            question_id: The unique identifier of the question to delete
            
        Returns:
            True if the deletion was successful, False otherwise
        """
        def delete_question_txn(transaction):
            # First delete any options
            transaction.execute_update(
                "DELETE FROM QuestionOptions WHERE question_id = @question_id",
                params={"question_id": question_id},
                param_types={"question_id": param_types.STRING}
            )
            
            # Then delete the question
            transaction.execute_update(
                "DELETE FROM RiskQuestions WHERE question_id = @question_id",
                params={"question_id": question_id},
                param_types={"question_id": param_types.STRING}
            )
        
        try:
            self.database.run_in_transaction(delete_question_txn)
            return True
        except Exception as e:
            print(f"Error deleting risk question: {e}")
            return False

    # No assessment-related functions needed

    # No search or metadata methods needed
