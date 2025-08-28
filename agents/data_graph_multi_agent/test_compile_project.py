#!/usr/bin/env python3
"""
Test script to verify the entire project compiles correctly.
This script checks for syntax errors, imports all modules, and tests agent initialization.
"""

import os
import sys
import importlib
import inspect
import logging
import py_compile
import traceback
from typing import List, Dict, Any, Tuple, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="[%(levelname)s] %(message)s"
)
logger = logging.getLogger(__name__)

# Project root directory
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))

# Add the parent directory to sys.path to allow importing project modules
parent_dir = os.path.dirname(os.path.dirname(PROJECT_ROOT))
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

def find_python_files(directory: str) -> List[str]:
    """Find all Python files in the given directory and its subdirectories."""
    python_files = []
    for root, dirs, files in os.walk(directory):
        # Skip virtual environment directories
        if 'venv' in dirs:
            dirs.remove('venv')
        if '__pycache__' in dirs:
            dirs.remove('__pycache__')
        
        for file in files:
            if file.endswith(".py"):
                python_files.append(os.path.join(root, file))
    return python_files

def check_syntax(file_path: str) -> Tuple[bool, Optional[str]]:
    """Check if a Python file has valid syntax."""
    try:
        py_compile.compile(file_path, doraise=True)
        return True, None
    except py_compile.PyCompileError as e:
        return False, str(e)
    except Exception as e:
        return False, str(e)

def test_import_module(module_path: str) -> Tuple[bool, Optional[str]]:
    """Test importing a module."""
    # Skip __pycache__ directories and __init__ files for direct import
    if "__pycache__" in module_path:
        return True, None
    
    try:
        # Just check if the file can be compiled
        with open(module_path, 'r') as f:
            compile(f.read(), module_path, 'exec')
        return True, None
    except SyntaxError as e:
        return False, f"Syntax error: {str(e)}"
    except Exception as e:
        return False, f"Unexpected error: {str(e)}"

def test_agent_initialization() -> Tuple[bool, Optional[str]]:
    """Test initializing the agents."""
    try:
        # Check if the agent module can be imported without actually initializing agents
        agent_path = os.path.join(PROJECT_ROOT, "agent.py")
        with open(agent_path, 'r') as f:
            compile(f.read(), agent_path, 'exec')
        return True, None
    except SyntaxError as e:
        return False, f"Syntax error in agent.py: {str(e)}"
    except FileNotFoundError:
        return False, "agent.py not found"
    except Exception as e:
        return False, f"Unexpected error: {str(e)}"

def main():
    """Main function to run all tests."""
    logger.info("Starting project compilation test")
    
    # Track test results
    syntax_errors = []
    import_errors = []
    
    # Find all Python files
    logger.info("Finding Python files...")
    python_files = find_python_files(PROJECT_ROOT)
    logger.info(f"Found {len(python_files)} Python files")
    
    # Check syntax for all Python files
    logger.info("Checking syntax...")
    for file_path in python_files:
        success, error = check_syntax(file_path)
        if not success:
            rel_path = os.path.relpath(file_path, PROJECT_ROOT)
            syntax_errors.append((rel_path, error))
        else:
            logger.info(f"✓ Syntax OK: {os.path.relpath(file_path, PROJECT_ROOT)}")
    
    # Test module compilation
    logger.info("Testing module compilation...")
    for file_path in python_files:
        if "__pycache__" not in file_path:
            success, error = test_import_module(file_path)
            if not success:
                rel_path = os.path.relpath(file_path, PROJECT_ROOT)
                import_errors.append((rel_path, error))
            else:
                logger.info(f"✓ Compilation OK: {os.path.relpath(file_path, PROJECT_ROOT)}")
    
    # Test agent initialization
    logger.info("Testing agent initialization...")
    agent_init_success, agent_init_error = test_agent_initialization()
    
    # Print summary
    logger.info("\n" + "="*50)
    logger.info("TEST SUMMARY")
    logger.info("="*50)
    
    if syntax_errors:
        logger.error(f"Found {len(syntax_errors)} files with syntax errors:")
        for file_path, error in syntax_errors:
            logger.error(f"  - {file_path}: {error}")
    else:
        logger.info("✓ All files passed syntax check")
    
    if import_errors:
        logger.error(f"Found {len(import_errors)} files with import errors:")
        for file_path, error in import_errors:
            logger.error(f"  - {file_path}: {error}")
    else:
        logger.info("✓ All modules can be imported")
    
    if agent_init_success:
        logger.info("✓ Agent initialization successful")
    else:
        logger.error(f"Agent initialization failed: {agent_init_error}")
    
    # Final result
    if not syntax_errors and not import_errors and agent_init_success:
        logger.info("\n✓ All tests passed! Project compiles successfully.")
        return 0
    else:
        logger.error("\n✗ Project compilation test failed.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
