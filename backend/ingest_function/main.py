import functions_framework
from flask import jsonify
import sys
import os

# Add the parent directory to the system path to find the 'services' package.
# This allows the Cloud Function to import the DataGraphService.
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from services.data_graph_service import DataGraphService

# --- Service Initialization ---
# Instantiate the service once globally. This allows for connection reuse.
try:
    data_graph_service = DataGraphService()
    print("DataGraphService initialized successfully in ingest function")
except Exception as e:
    print(f"WARNING: DataGraphService initialization failed: {e}")
    data_graph_service = None

@functions_framework.http
def ingest_document(request):
    """HTTP Cloud Function to ingest a document using the DataGraphService."""
    # Handle CORS preflight requests
    if request.method == 'OPTIONS':
        headers = {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'POST, OPTIONS',
            'Access-Control-Allow-Headers': 'Content-Type',
            'Access-Control-Max-Age': '3600'
        }
        return ('', 204, headers)

    headers = {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'POST, OPTIONS',
        'Access-Control-Allow-Headers': 'Content-Type'
    }
    
    # Check if service is initialized
    if data_graph_service is None or not data_graph_service.database:
        return (jsonify({'error': 'Service not initialized. Check environment variables and GCP configuration.'}), 500, headers)
    
    if 'file' not in request.files:
        return (jsonify({'error': 'No file part in the request'}), 400, headers)

    file = request.files['file']
    if file.filename == '':
        return (jsonify({'error': 'No file selected for uploading'}), 400, headers)

    try:
        print(f"Processing file: {file.filename}, size: {len(file.read())} bytes")
        file.seek(0)  # Reset file pointer after reading for size
        document_text = file.read().decode('utf-8')
        print(f"Document text length: {len(document_text)} characters")
        
        result = data_graph_service.ingest_document(document_text)
        print(f"Ingestion result: {result}")
        
        response_data = {
            'success': True, 
            'filename': file.filename, 
            'nodes_found': result.get('nodes_found', 0), 
            'relationships_found': result.get('relationships_found', 0),
            'message': 'Document ingested successfully'
        }
        return (jsonify(response_data), 200, headers)

    except ValueError as ve:
        # Handle cases where the document is invalid or graph extraction fails
        print(f"ValueError in document processing: {ve}")
        return (jsonify({'error': str(ve)}), 422, headers) # Unprocessable Entity
    except Exception as e:
        print(f"Error processing file: {e}")
        import traceback
        traceback.print_exc()
        return (jsonify({'error': f'An internal error occurred: {str(e)}'}), 500, headers)