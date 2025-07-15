#!/usr/bin/env python3
"""
Test file upload functionality to identify the issue
"""

import requests
import os
from pathlib import Path

def test_file_upload():
    """Test the training document upload endpoint"""
    
    # Base URL for the API
    base_url = "http://localhost:8000"
    
    # Test file path
    test_file_path = "../test_documents/ai_soul_knowledge_base.txt"
    
    if not os.path.exists(test_file_path):
        print(f"❌ Test file not found: {test_file_path}")
        return
    
    # First, let's test the endpoint directly with curl-like request
    url = f"{base_url}/api/v1/training/test-soul-id/documents"
    
    try:
        # Prepare the file and form data
        with open(test_file_path, 'rb') as f:
            files = {
                'file': ('ai_soul_knowledge_base.txt', f, 'text/plain')
            }
            data = {
                'description': 'Test training document'
            }
            
            # Make the request (this will fail due to auth, but we can see the error)
            response = requests.post(url, files=files, data=data)
            
            print(f"Status Code: {response.status_code}")
            print(f"Response: {response.text}")
            
            if response.status_code == 422:
                print("✅ Endpoint is working, validation error is expected without auth")
            elif response.status_code == 401:
                print("✅ Endpoint is working, auth error is expected")
            else:
                print(f"❌ Unexpected response: {response.status_code}")
                
    except Exception as e:
        print(f"❌ Error testing upload: {str(e)}")

def test_openapi_generation():
    """Test OpenAPI spec generation"""
    try:
        # Check if we can access the OpenAPI docs
        response = requests.get("http://localhost:8000/docs")
        if response.status_code == 200:
            print("✅ FastAPI docs are accessible")
        else:
            print(f"❌ Cannot access docs: {response.status_code}")
            
        # Check OpenAPI JSON
        response = requests.get("http://localhost:8000/openapi.json")
        if response.status_code == 200:
            openapi_spec = response.json()
            
            # Check if training upload endpoint exists
            paths = openapi_spec.get('paths', {})
            training_upload_path = None
            
            for path, methods in paths.items():
                if 'training' in path and 'documents' in path and 'post' in methods:
                    training_upload_path = path
                    break
            
            if training_upload_path:
                print(f"✅ Training upload endpoint found: {training_upload_path}")
                
                # Check the request body schema
                post_method = paths[training_upload_path]['post']
                request_body = post_method.get('requestBody', {})
                content = request_body.get('content', {})
                
                if 'multipart/form-data' in content:
                    print("✅ Multipart form data is correctly configured")
                    schema = content['multipart/form-data'].get('schema', {})
                    properties = schema.get('properties', {})
                    
                    if 'file' in properties:
                        print("✅ File field is defined in schema")
                    else:
                        print("❌ File field is missing from schema")
                        print(f"Available fields: {list(properties.keys())}")
                else:
                    print("❌ Multipart form data not configured")
                    print(f"Available content types: {list(content.keys())}")
            else:
                print("❌ Training upload endpoint not found")
                print("Available paths:")
                for path in paths.keys():
                    if 'training' in path:
                        print(f"  - {path}")
        else:
            print(f"❌ Cannot access OpenAPI spec: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error checking OpenAPI: {str(e)}")

if __name__ == "__main__":
    print("🧪 Testing file upload functionality...")
    print("\n1. Testing OpenAPI specification...")
    test_openapi_generation()
    
    print("\n2. Testing file upload endpoint...")
    test_file_upload()
    
    print("\n📋 Recommendations:")
    print("1. Start the backend server: uvicorn app.main:app --reload")
    print("2. Check the frontend FormData creation")
    print("3. Regenerate the frontend client if needed") 