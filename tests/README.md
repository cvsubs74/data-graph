# Privacy Data Governance Graph - Test Suite

This directory contains comprehensive tests for the Privacy Data Governance Graph backend, including unit tests, integration tests, and MCP client tests.

## Test Structure

```
tests/
├── README.md                 # This file
├── requirements.txt          # Test dependencies
├── run_tests.sh             # Test runner script
├── simple_test.py           # HTTP integration tests
├── test_mcp_client.py       # MCP client tests (comprehensive CRUD)
└── test_suite.py            # Unit tests and end-to-end tests
```

## Quick Start

### 1. Run All Tests
```bash
cd tests
./run_tests.sh
```

### 2. Run Specific Test Types
```bash
# Integration tests only
./run_tests.sh integration

# MCP client tests only
./run_tests.sh mcp

# Unit tests only
./run_tests.sh unit
```

## Test Types

### Integration Tests (`simple_test.py`)
- Tests deployed Cloud Functions via HTTP
- Validates MCP function health and tools endpoints
- Tests ingest function CORS and document upload
- Uses only Python standard library

### MCP Client Tests (`test_mcp_client.py`)
- Comprehensive testing of all 30 CRUD operations
- Tests all entity types: Assets, Processing Activities, Data Elements, Data Subject Types, Vendors
- Tests relationship creation and management
- Uses FastMCP client for authentic MCP protocol testing

### Unit Tests (`test_suite.py`)
- Direct testing of DataGraphService methods
- End-to-end workflow testing
- Requires access to Google Cloud resources

## Environment Setup

The test runner automatically:
1. Creates a Python virtual environment (`tests/venv/`)
2. Installs all required dependencies
3. Sets up proper Python paths
4. Runs the specified tests

## Test Configuration

Tests are configured to use the deployed Cloud Functions:
- **Ingest Function**: `https://ingest-function-pt7snlxyuq-uc.a.run.app`
- **MCP Function**: `https://mcp-function-pt7snlxyuq-uc.a.run.app`

## Dependencies

- `requests` - HTTP client for integration tests
- `fastmcp` - MCP client for protocol testing
- `google-cloud-*` - Google Cloud SDK libraries for unit tests
- `pytest` - Testing framework
- `pytest-asyncio` - Async test support

## Test Results

Each test suite provides detailed output including:
- Individual test results (✅ PASS / ❌ FAIL)
- Summary statistics
- Error details for failed tests
- Cleanup confirmation for created test data

## Troubleshooting

### Virtual Environment Issues
```bash
# Remove and recreate venv
rm -rf tests/venv
./run_tests.sh
```

### Dependency Issues
```bash
# Update requirements
cd tests
source venv/bin/activate
pip install --upgrade -r requirements.txt
```

### Cloud Function Access Issues
- Ensure Cloud Functions are deployed and accessible
- Check function URLs in test configuration
- Verify GCP project permissions

## Contributing

When adding new tests:
1. Add test dependencies to `requirements.txt`
2. Update this README with new test descriptions
3. Ensure tests clean up any created resources
4. Follow the existing naming and structure conventions
