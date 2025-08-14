#!/usr/bin/env python3
"""
HTTP integration tests for Privacy Data Governance Graph MCP Server
Tests target the deployed HTTP endpoint for liveness, tool discovery, and basic functionality.
"""

import asyncio
import time
import unittest
import uuid
from typing import Dict, List, Any

from fastmcp import Client

# MCP server URL - update this to match your deployment
MCP_SERVER_URL = "https://mcp-server-79797180773.us-central1.run.app/mcp"

class TestMCPServer(unittest.IsolatedAsyncioTestCase):
    """HTTP integration tests for the deployed MCP server."""
    
    async def asyncSetUp(self):
        """Set up the test client before each test."""
        self.client = Client(MCP_SERVER_URL)
        self.connection = await self.client.__aenter__()
        print(f"\nConnected to MCP server at {MCP_SERVER_URL}")
    
    async def asyncTearDown(self):
        """Clean up after each test."""
        await self.client.__aexit__(None, None, None)
        print("Disconnected from MCP server")
    
    async def test_01_server_connectivity(self):
        """Test basic server connectivity with ping."""
        print("\n--- Testing Server Connectivity ---")
        start_time = time.time()
        await self.client.ping()
        elapsed = time.time() - start_time
        print(f"Ping successful in {elapsed:.4f} seconds")
        self.assertTrue(True)  # If we got here, ping succeeded
    
    async def test_02_list_tools(self):
        """Test listing available tools."""
        print("\n--- Testing Tool Discovery ---")
        tools = await self.client.list_tools()
        print(f"Found {len(tools)} tools:")
        for tool in tools:
            description = tool.description.split('.')[0] if tool.description else 'No description'
            print(f"- {tool.name}: {description}")
        
        # Verify expected tools exist
        tool_names = [tool.name for tool in tools]
        expected_tools = [
            'create_asset', 'get_asset', 'update_asset', 'delete_asset', 'list_assets',
            'create_processing_activity', 'get_processing_activity', 'list_processing_activities', 'delete_processing_activity',
            'create_data_element', 'get_data_element', 'list_data_elements', 'delete_data_element',
            'create_relationship', 'get_relationships', 'delete_relationship'
        ]
        
        for expected_tool in expected_tools:
            self.assertIn(expected_tool, tool_names, f"Expected tool '{expected_tool}' not found")
        
        print(f"✅ All {len(expected_tools)} expected tools found")
    
    async def test_03_basic_asset_operations(self):
        """Test basic asset operations to verify functionality."""
        print("\n--- Testing Basic Asset Operations ---")
        
        # Test data
        test_asset_name = f"HTTP Test Asset {uuid.uuid4().hex[:8]}"
        test_description = "Asset created during HTTP integration testing"
        
        asset_id = None
        
        try:
            # Test 1: Create Asset
            print(f"Creating asset: {test_asset_name}")
            create_result = await self.client.call_tool("create_asset", {
                "name": test_asset_name,
                "description": test_description,
                "properties": {"test": True, "source": "http_integration_test"}
            })
            
            asset_id = create_result.data
            self.assertIsNotNone(asset_id, "Asset creation should return an ID")
            print(f"✅ Asset created with ID: {asset_id}")
            
            # Test 2: Get Asset
            print(f"Retrieving asset: {asset_id}")
            get_result = await self.client.call_tool("get_asset", {"asset_id": asset_id})
            
            retrieved_asset = get_result.data
            self.assertIsNotNone(retrieved_asset, "Should retrieve the created asset")
            print(f"✅ Asset retrieved successfully")
            
            # Test 3: List Assets (verify our asset exists)
            print("Listing assets to verify our asset exists")
            list_result = await self.client.call_tool("list_assets", {"limit": 100})
            assets_list = list_result.data
            
            self.assertIsNotNone(assets_list, "Should get a list of assets")
            self.assertIsInstance(assets_list, list, "Assets list should be a list")
            print(f"✅ Assets list retrieved with {len(assets_list)} items")
            
        finally:
            # Clean up - Delete Asset
            if asset_id:
                print(f"Cleaning up: deleting asset {asset_id}")
                try:
                    delete_result = await self.client.call_tool("delete_asset", {"asset_id": asset_id})
                    delete_success = delete_result.data
                    if delete_success:
                        print(f"✅ Asset {asset_id} deleted successfully")
                    else:
                        print(f"⚠️  Asset {asset_id} deletion may have failed")
                except Exception as e:
                    print(f"⚠️  Error during cleanup: {e}")
    
    async def test_04_processing_activity_operations(self):
        """Test basic processing activity operations."""
        print("\n--- Testing Processing Activity Operations ---")
        
        # Test data
        test_activity_name = f"HTTP Test Activity {uuid.uuid4().hex[:8]}"
        test_description = "Processing activity created during HTTP integration testing"
        test_purpose = "HTTP integration testing"
        
        activity_id = None
        
        try:
            # Test 1: Create Processing Activity
            print(f"Creating processing activity: {test_activity_name}")
            create_result = await self.client.call_tool("create_processing_activity", {
                "name": test_activity_name,
                "description": test_description,
                "purpose": test_purpose,
                "legal_basis": "Consent"
            })
            
            activity_id = create_result.data
            self.assertIsNotNone(activity_id, "Processing activity creation should return an ID")
            print(f"✅ Processing activity created with ID: {activity_id}")
            
            # Test 2: Get Processing Activity
            print(f"Retrieving processing activity: {activity_id}")
            get_result = await self.client.call_tool("get_processing_activity", {"activity_id": activity_id})
            
            retrieved_activity = get_result.data
            self.assertIsNotNone(retrieved_activity, "Should retrieve the created processing activity")
            print(f"✅ Processing activity retrieved successfully")
            
            # Test 3: List Processing Activities
            print("Listing processing activities")
            list_result = await self.client.call_tool("list_processing_activities", {"limit": 100})
            activities_list = list_result.data
            
            self.assertIsNotNone(activities_list, "Should get a list of processing activities")
            self.assertIsInstance(activities_list, list, "Activities list should be a list")
            print(f"✅ Processing activities list retrieved with {len(activities_list)} items")
            
        finally:
            # Clean up - Delete Processing Activity
            if activity_id:
                print(f"Cleaning up: deleting processing activity {activity_id}")
                try:
                    delete_result = await self.client.call_tool("delete_processing_activity", {"activity_id": activity_id})
                    delete_success = delete_result.data
                    if delete_success:
                        print(f"✅ Processing activity {activity_id} deleted successfully")
                    else:
                        print(f"⚠️  Processing activity {activity_id} deletion may have failed")
                except Exception as e:
                    print(f"⚠️  Error during cleanup: {e}")
    
    async def test_05_data_element_operations(self):
        """Test basic data element operations."""
        print("\n--- Testing Data Element Operations ---")
        
        # Test data
        test_element_name = f"HTTP Test Data Element {uuid.uuid4().hex[:8]}"
        test_description = "Data element created during HTTP integration testing"
        test_data_type = "PII"
        
        element_id = None
        
        try:
            # Test 1: Create Data Element
            print(f"Creating data element: {test_element_name}")
            create_result = await self.client.call_tool("create_data_element", {
                "name": test_element_name,
                "description": test_description,
                "data_type": test_data_type
            })
            
            element_id = create_result.data
            self.assertIsNotNone(element_id, "Data element creation should return an ID")
            print(f"✅ Data element created with ID: {element_id}")
            
            # Test 2: Get Data Element
            print(f"Retrieving data element: {element_id}")
            get_result = await self.client.call_tool("get_data_element", {"element_id": element_id})
            
            retrieved_element = get_result.data
            self.assertIsNotNone(retrieved_element, "Should retrieve the created data element")
            print(f"✅ Data element retrieved successfully")
            
            # Test 3: List Data Elements
            print("Listing data elements")
            list_result = await self.client.call_tool("list_data_elements", {"limit": 100})
            elements_list = list_result.data
            
            self.assertIsNotNone(elements_list, "Should get a list of data elements")
            self.assertIsInstance(elements_list, list, "Elements list should be a list")
            print(f"✅ Data elements list retrieved with {len(elements_list)} items")
            
        finally:
            # Clean up - Delete Data Element
            if element_id:
                print(f"Cleaning up: deleting data element {element_id}")
                try:
                    delete_result = await self.client.call_tool("delete_data_element", {"element_id": element_id})
                    delete_success = delete_result.data
                    if delete_success:
                        print(f"✅ Data element {element_id} deleted successfully")
                    else:
                        print(f"⚠️  Data element {element_id} deletion may have failed")
                except Exception as e:
                    print(f"⚠️  Error during cleanup: {e}")
    
    async def test_06_relationship_operations(self):
        """Test basic relationship operations."""
        print("\n--- Testing Relationship Operations ---")
        
        # Create test entities first
        asset_result = await self.client.call_tool("create_asset", {
            "name": f"HTTP Relationship Test Asset {uuid.uuid4().hex[:8]}",
            "description": "Asset for HTTP relationship testing"
        })
        asset_id = asset_result.data
        print(f"Created test asset: {asset_id}")
        
        activity_result = await self.client.call_tool("create_processing_activity", {
            "name": f"HTTP Relationship Test Activity {uuid.uuid4().hex[:8]}",
            "description": "Activity for HTTP relationship testing",
            "purpose": "Testing relationships via HTTP"
        })
        activity_id = activity_result.data
        print(f"Created test activity: {activity_id}")
        
        try:
            # Test 1: Create Relationship
            print(f"Creating relationship between asset {asset_id} and activity {activity_id}")
            create_rel_result = await self.client.call_tool("create_relationship", {
                "from_entity_id": asset_id,
                "to_entity_id": activity_id,
                "relationship_type": "used_in",
                "properties": {"test": True, "source": "http_integration_test"}
            })
            
            relationship_success = create_rel_result.data
            self.assertTrue(relationship_success, "Relationship creation should succeed")
            print(f"✅ Relationship created successfully")
            
            # Test 2: Get Relationships
            print(f"Getting relationships for asset {asset_id}")
            get_rel_result = await self.client.call_tool("get_relationships", {"entity_id": asset_id})
            
            relationships = get_rel_result.data
            self.assertIsNotNone(relationships, "Should get relationships for the entity")
            self.assertIsInstance(relationships, list, "Relationships should be a list")
            print(f"✅ Relationships retrieved: {len(relationships)} relationships found")
            
            # Test 3: Delete Relationship
            print(f"Deleting relationship between asset {asset_id} and activity {activity_id}")
            delete_rel_result = await self.client.call_tool("delete_relationship", {
                "source_id": asset_id,
                "target_id": activity_id
            })
            
            delete_success = delete_rel_result.data
            self.assertTrue(delete_success, "Relationship deletion should succeed")
            print(f"✅ Relationship deleted successfully")
            
            # Test 4: Verify Relationship Deletion
            print(f"Verifying relationship deletion for asset {asset_id}")
            verify_result = await self.client.call_tool("get_relationships", {"entity_id": asset_id})
            
            remaining_relationships = verify_result.data
            # Check if the relationship was actually deleted
            target_relationships = [r for r in remaining_relationships if r.get('target_id') == activity_id]
            self.assertEqual(len(target_relationships), 0, "Relationship should be deleted")
            print(f"✅ Relationship deletion verified")
            
        finally:
            # Clean up test entities
            try:
                await self.client.call_tool("delete_asset", {"asset_id": asset_id})
                print(f"Cleaned up test asset: {asset_id}")
            except Exception as e:
                print(f"Error cleaning up asset: {e}")
            
            try:
                await self.client.call_tool("delete_processing_activity", {"activity_id": activity_id})
                print(f"Cleaned up test activity: {activity_id}")
            except Exception as e:
                print(f"Error cleaning up activity: {e}")

async def run_tests():
    """Run all tests in the test suite."""
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(TestMCPServer)
    runner = unittest.TextTestRunner(verbosity=2)
    result = await asyncio.to_thread(runner.run, suite)
    return result.wasSuccessful()

if __name__ == "__main__":
    print(f"Starting HTTP integration tests for Privacy Data Governance Graph MCP server")
    print(f"Server URL: {MCP_SERVER_URL}")
    print("=" * 80)
    
    success = asyncio.run(run_tests())
    
    print("=" * 80)
    if success:
        print("🎉 All HTTP integration tests passed!")
    else:
        print("❌ Some HTTP integration tests failed. Check the output above.")
    
    print("HTTP integration testing completed!")
