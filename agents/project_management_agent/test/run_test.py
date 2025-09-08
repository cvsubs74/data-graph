#!/usr/bin/env python3
"""Test script for the project management agent using local test documents."""

import os
import argparse
import logging
import sys
from pathlib import Path

# Add the parent directory to the path so we can import the agent modules
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from agents.project_management_agent.document_parser import parse_document
from agents.project_management_agent.entity_detector import detect_entities
from agents.project_management_agent.project_analyzer import analyze_project
from agents.project_management_agent.agent import root_agent
from google.adk.run import Runner

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Get the absolute path to the test documents directory
TEST_DOCS_DIR = Path(__file__).parent / "documents"

def serve_local_file(file_path):
    """
    Create a simple HTTP server to serve a local file for testing.
    
    Args:
        file_path: Path to the file to serve
        
    Returns:
        str: URL to access the file
    """
    import http.server
    import socketserver
    import threading
    import tempfile
    import shutil
    
    # Create a temporary directory
    temp_dir = tempfile.mkdtemp()
    
    # Copy the file to the temporary directory
    temp_file_path = os.path.join(temp_dir, os.path.basename(file_path))
    shutil.copy2(file_path, temp_file_path)
    
    # Set up the server
    PORT = 8000
    Handler = http.server.SimpleHTTPRequestHandler
    
    # Change to the temporary directory
    os.chdir(temp_dir)
    
    # Create the server
    httpd = socketserver.TCPServer(("", PORT), Handler)
    
    # Start the server in a separate thread
    server_thread = threading.Thread(target=httpd.serve_forever)
    server_thread.daemon = True
    server_thread.start()
    
    logger.info(f"Serving {os.path.basename(file_path)} at http://localhost:{PORT}/{os.path.basename(file_path)}")
    
    return f"http://localhost:{PORT}/{os.path.basename(file_path)}"

def test_document_parser(document_path):
    """Test the document parser agent with a local document.
    
    Args:
        document_path: Path to the document to parse
        
    Returns:
        dict: Parsed document data
    """
    logger.info(f"Testing document parser with file: {document_path}")
    
    # Serve the document locally
    document_url = serve_local_file(document_path)
    
    # Parse the document
    result = parse_document(document_url)
    
    logger.info(f"Document parsing result: {result['status']}")
    return result

def test_entity_detector(parsed_document):
    """Test the entity detector agent.
    
    Args:
        parsed_document: Parsed document data
        
    Returns:
        dict: Detected entities data
    """
    logger.info("Testing entity detector")
    
    # Detect entities
    result = detect_entities(parsed_document)
    
    logger.info(f"Entity detection result: {result['status']}")
    return result

def test_project_analyzer(detected_entities, project_context=None):
    """Test the project analyzer agent.
    
    Args:
        detected_entities: Detected entities data
        project_context: Optional additional project context
        
    Returns:
        dict: Project analysis data
    """
    logger.info("Testing project analyzer")
    
    # Analyze project
    result = analyze_project(detected_entities, project_context)
    
    logger.info(f"Project analysis result: {result['status']}")
    return result

def test_full_workflow(document_path, project_context=None):
    """Test the full workflow from document parsing to project analysis.
    
    Args:
        document_path: Path to the document to parse
        project_context: Optional additional project context
    """
    logger.info(f"Testing full workflow with document: {document_path}")
    
    # Parse document
    parsed_document = test_document_parser(document_path)
    
    # Detect entities
    detected_entities = test_entity_detector(parsed_document)
    
    # Analyze project
    project_analysis = test_project_analyzer(detected_entities, project_context)
    
    logger.info("Full workflow test completed")
    return project_analysis

def test_orchestrator(document_path, project_context=None):
    """Test the orchestrator agent with a local document.
    
    Args:
        document_path: Path to the document to parse
        project_context: Optional additional project context
    """
    logger.info(f"Testing orchestrator with document: {document_path}")
    
    # Serve the document locally
    document_url = serve_local_file(document_path)
    
    # Create a runner for the root agent
    runner = Runner(root_agent)
    
    # Run the agent
    input_message = (
        f"Please analyze the project document at {document_url}. "
        f"Extract entities and provide a privacy governance analysis. "
    )
    
    if project_context:
        input_message += f"\n\nAdditional project context: {project_context}"
    
    runner.run(input_message)
    
    logger.info("Orchestrator test completed")

def main():
    """Main entry point for the test script."""
    parser = argparse.ArgumentParser(description="Test the project management agent with local documents")
    parser.add_argument("--document", type=str, choices=["project", "vendor", "processing", "all"], 
                        default="project", help="Document to test with")
    parser.add_argument("--mode", type=str, default="orchestrator", 
                        choices=["parser", "detector", "analyzer", "full", "orchestrator"],
                        help="Test mode")
    parser.add_argument("--context", type=str, help="Optional additional project context")
    
    args = parser.parse_args()
    
    # Map document choices to file paths
    document_map = {
        "project": TEST_DOCS_DIR / "project_initiative.txt",
        "vendor": TEST_DOCS_DIR / "vendor_assessment.txt",
        "processing": TEST_DOCS_DIR / "data_processing_inventory.txt"
    }
    
    if args.document == "all":
        # Test with all documents
        for doc_name, doc_path in document_map.items():
            logger.info(f"Testing with {doc_name} document")
            if args.mode == "orchestrator":
                test_orchestrator(doc_path, args.context)
            elif args.mode == "full":
                test_full_workflow(doc_path, args.context)
            elif args.mode == "parser":
                test_document_parser(doc_path)
            else:
                # For other modes, we need to run the full workflow up to that point
                parsed_document = test_document_parser(doc_path)
                if args.mode in ["detector", "analyzer"]:
                    detected_entities = test_entity_detector(parsed_document)
                    if args.mode == "analyzer":
                        test_project_analyzer(detected_entities, args.context)
    else:
        # Test with a single document
        doc_path = document_map[args.document]
        if args.mode == "orchestrator":
            test_orchestrator(doc_path, args.context)
        elif args.mode == "full":
            test_full_workflow(doc_path, args.context)
        elif args.mode == "parser":
            test_document_parser(doc_path)
        else:
            # For other modes, we need to run the full workflow up to that point
            parsed_document = test_document_parser(doc_path)
            if args.mode in ["detector", "analyzer"]:
                detected_entities = test_entity_detector(parsed_document)
                if args.mode == "analyzer":
                    test_project_analyzer(detected_entities, args.context)

if __name__ == "__main__":
    main()
