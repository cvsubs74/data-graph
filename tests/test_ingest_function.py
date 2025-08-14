#!/usr/bin/env python3
"""
Ingest Function Integration Tests
Tests the document ingestion Cloud Function for CORS and document upload functionality.
"""

import json
import os
import urllib.request
import urllib.parse

# Test configuration
TEST_CONFIG = {
    'ingest_function_url': 'https://ingest-function-pt7snlxyuq-uc.a.run.app',
    'timeout': 30
}

def test_ingest_function_cors():
    """Test ingest function CORS preflight."""
    print("🔍 Testing Ingest Function CORS...")
    
    try:
        req = urllib.request.Request(TEST_CONFIG['ingest_function_url'], method='OPTIONS')
        with urllib.request.urlopen(req, timeout=TEST_CONFIG['timeout']) as response:
            if response.status == 204:
                headers = dict(response.headers)
                # Convert headers to lowercase for case-insensitive comparison
                headers_lower = {k.lower(): v for k, v in headers.items()}
                
                cors_origin = headers_lower.get('access-control-allow-origin', 'Not set')
                print(f"✅ Ingest Function CORS: {cors_origin}")
                
                # Validate CORS headers (case-insensitive)
                assert 'access-control-allow-origin' in headers_lower, "CORS header missing"
                assert headers_lower['access-control-allow-origin'] == '*', "CORS not allowing all origins"
                
                return True
            else:
                print(f"❌ Ingest Function CORS failed with status: {response.status}")
                return False
    except Exception as e:
        print(f"❌ Ingest Function CORS test failed: {e}")
        return False

def test_ingest_function_document():
    """Test document ingestion via ingest function."""
    print("🔍 Testing Ingest Function Document Upload...")
    
    # Read a test document
    test_file_path = os.path.join(os.path.dirname(__file__), 'data', 'comprehensive_privacy_policy.txt')
    
    if not os.path.exists(test_file_path):
        print(f"⚠️  Test file not found: {test_file_path}, skipping document upload test")
        return True
    
    try:
        with open(test_file_path, 'r') as f:
            file_content = f.read()
        
        # Create multipart form data
        boundary = '----WebKitFormBoundary7MA4YWxkTrZu0gW'
        body = (
            f'--{boundary}\r\n'
            f'Content-Disposition: form-data; name="file"; filename="test_privacy_policy.txt"\r\n'
            f'Content-Type: text/plain\r\n\r\n'
            f'{file_content}\r\n'
            f'--{boundary}--\r\n'
        ).encode('utf-8')
        
        # Create request
        req = urllib.request.Request(
            TEST_CONFIG['ingest_function_url'],
            data=body,
            method='POST'
        )
        req.add_header('Content-Type', f'multipart/form-data; boundary={boundary}')
        
        # Send request
        with urllib.request.urlopen(req, timeout=TEST_CONFIG['timeout']) as response:
            if response.status == 200:
                data = json.loads(response.read().decode())
                print(f"✅ Document Ingestion: {data.get('message', 'Success')}")
                
                # Validate response
                assert 'message' in data, "Response missing message field"
                assert 'success' in data.get('message', '').lower() or 'ingested' in data.get('message', '').lower(), "Document ingestion may have failed"
                
                return True
            else:
                print(f"❌ Document ingestion failed with status: {response.status}")
                return False
                
    except Exception as e:
        print(f"❌ Ingest Function Document test failed: {e}")
        return False

def test_ingest_function_health():
    """Test ingest function basic health check via OPTIONS request."""
    print("🔍 Testing Ingest Function Health...")
    
    try:
        # Test OPTIONS request to ingest function (CORS preflight also validates function is running)
        req = urllib.request.Request(TEST_CONFIG['ingest_function_url'], method='OPTIONS')
        with urllib.request.urlopen(req, timeout=TEST_CONFIG['timeout']) as response:
            if response.status == 204:
                print("✅ Ingest Function Health: Function is responding to requests")
                return True
            else:
                print(f"❌ Ingest Function Health failed with status: {response.status}")
                return False
    except Exception as e:
        print(f"❌ Ingest Function Health test failed: {e}")
        return False

def run_all_tests():
    """Run all ingest function tests."""
    print("=" * 60)
    print("INGEST FUNCTION INTEGRATION TESTS")
    print("=" * 60)
    
    tests = [
        ("Ingest Function Health", test_ingest_function_health),
        ("Ingest Function CORS", test_ingest_function_cors),
        ("Ingest Function Document Upload", test_ingest_function_document),
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n--- {test_name} ---")
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    print(f"Tests run: {total}")
    print(f"Passed: {passed}")
    print(f"Failed: {total - passed}")
    print(f"Success rate: {(passed/total)*100:.1f}%")
    
    print("\nDetailed Results:")
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {status} - {test_name}")
    
    if passed == total:
        print("\n🎉 All ingest function tests passed!")
        return True
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. Please check the logs above.")
        return False

if __name__ == "__main__":
    success = run_all_tests()
    exit(0 if success else 1)
