#!/usr/bin/env python3
"""
Integration Test for Streamlit Frontend and FastAPI Backend
==========================================================

This script tests the integration between the Streamlit frontend
and the FastAPI backend to ensure all components work together.
"""

import requests
import json
import time
from typing import Dict, Any

def test_api_endpoint(endpoint: str, data: Dict[str, Any]) -> bool:
    """Test a specific API endpoint"""
    
    try:
        print(f"Testing endpoint: {endpoint}")
        print(f"Request data: {json.dumps(data, indent=2)}")
        
        start_time = time.time()
        response = requests.post(
            endpoint,
            json=data,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        response_time = time.time() - start_time
        
        print(f"Response time: {response_time:.2f}s")
        print(f"Status code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"Response keys: {list(result.keys())}")
            print("✅ Test PASSED")
            return True
        else:
            print(f"❌ Test FAILED: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Test FAILED with exception: {e}")
        return False

def test_server_connectivity():
    """Test basic server connectivity"""
    
    print("=" * 60)
    print("TESTING SERVER CONNECTIVITY")
    print("=" * 60)
    
    try:
        response = requests.get("http://localhost:8003/docs", timeout=5)
        if response.status_code == 200:
            print("✅ FastAPI server is accessible")
            return True
        else:
            print(f"❌ FastAPI server returned status: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Cannot connect to FastAPI server: {e}")
        return False

def test_byteplus_endpoints():
    """Test BytePlus generation endpoints"""
    
    print("\n" + "=" * 60)
    print("TESTING BYTEPLUS GENERATION ENDPOINTS")
    print("=" * 60)
    
    base_url = "http://localhost:8003"
    
    # Test cases for different generation types
    test_cases = [
        {
            "name": "Text2Img Single",
            "endpoint": f"{base_url}/byteplus-generate",
            "data": {
                "generation_type": "text2img_single",
                "prompt": "A beautiful sunset over mountains",
                "image_size": "512x512",
                "num_images": 1,
                "style": "realistic"
            }
        },
        {
            "name": "Text2Img Multiple",
            "endpoint": f"{base_url}/byteplus-generate",
            "data": {
                "generation_type": "text2img_multiple",
                "prompt": "A cute cat playing in a garden",
                "image_size": "512x512",
                "num_images": 3,
                "style": "cartoon"
            }
        }
    ]
    
    results = []
    
    for test_case in test_cases:
        print(f"\n--- Testing {test_case['name']} ---")
        success = test_api_endpoint(test_case['endpoint'], test_case['data'])
        results.append((test_case['name'], success))
        time.sleep(1)  # Brief pause between tests
    
    return results

def test_streamlit_components():
    """Test Streamlit component imports"""
    
    print("\n" + "=" * 60)
    print("TESTING STREAMLIT COMPONENT IMPORTS")
    print("=" * 60)
    
    try:
        # Test main app import
        print("Testing main app import...")
        import streamlit_app
        print("✅ Main app imports successfully")
        
        # Test component imports
        print("Testing component imports...")
        from components.byteplus_interface import render_byteplus_generation_interface
        from components.performance_metrics import render_performance_overview
        from components.responsive_layout import ErrorHandler
        from components.visualization import RealTimeVisualizer
        print("✅ All components import successfully")
        
        return True
        
    except Exception as e:
        print(f"❌ Component import failed: {e}")
        return False

def run_integration_tests():
    """Run complete integration test suite"""
    
    print("🚀 STARTING INTEGRATION TESTS")
    print("=" * 60)
    
    # Test 1: Server connectivity
    server_ok = test_server_connectivity()
    
    # Test 2: Component imports
    components_ok = test_streamlit_components()
    
    # Test 3: API endpoints
    if server_ok:
        api_results = test_byteplus_endpoints()
        api_ok = all(result[1] for result in api_results)
    else:
        api_ok = False
        api_results = []
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    print(f"Server Connectivity: {'✅ PASS' if server_ok else '❌ FAIL'}")
    print(f"Component Imports: {'✅ PASS' if components_ok else '❌ FAIL'}")
    print(f"API Endpoints: {'✅ PASS' if api_ok else '❌ FAIL'}")
    
    if api_results:
        print("\nAPI Test Details:")
        for name, success in api_results:
            print(f"  - {name}: {'✅ PASS' if success else '❌ FAIL'}")
    
    overall_success = server_ok and components_ok and api_ok
    
    print(f"\nOverall Result: {'🎉 ALL TESTS PASSED' if overall_success else '⚠️ SOME TESTS FAILED'}")
    
    if overall_success:
        print("\n🎯 Integration is working correctly!")
        print("You can now use the Streamlit interface at: http://localhost:8501")
    else:
        print("\n🔧 Please check the failed components before using the interface.")
    
    return overall_success

if __name__ == "__main__":
    run_integration_tests()