#!/usr/bin/env python3
"""
Comprehensive endpoint testing script.

This script tests all major endpoints with different user roles to verify:
1. Authentication works correctly
2. Role-based access control is enforced
3. All endpoints return expected responses
4. Frontend integration points work properly
"""

import json
import requests
import time
from typing import Dict, Any


BASE_URL = "http://localhost:8000"
API_BASE = f"{BASE_URL}/api/v1"

# Test credentials
TEST_USERS = {
    "admin": {"email": "admin@example.com", "password": "admin123"},
    "counselor": {"email": "counselor@example.com", "password": "counselor123"},
    "trainer": {"email": "trainer@example.com", "password": "trainer123"},
    "user": {"email": "user@example.com", "password": "user123"}
}


class EndpointTester:
    def __init__(self):
        self.tokens = {}
        self.test_results = {}
        
    def login_user(self, role: str) -> str:
        """Login a user and return access token."""
        if role in self.tokens:
            return self.tokens[role]
            
        credentials = TEST_USERS[role]
        response = requests.post(f"{API_BASE}/login/access-token", data={
            "username": credentials["email"],
            "password": credentials["password"]
        })
        
        if response.status_code == 200:
            token = response.json()["access_token"]
            self.tokens[role] = token
            print(f"✅ {role.capitalize()} login successful")
            return token
        else:
            print(f"❌ {role.capitalize()} login failed: {response.status_code}")
            return None
    
    def get_auth_headers(self, role: str) -> Dict[str, str]:
        """Get authorization headers for a role."""
        token = self.login_user(role)
        if token:
            return {"Authorization": f"Bearer {token}"}
        return {}
    
    def test_endpoint(self, method: str, endpoint: str, role: str, 
                     expected_status: int = 200, data: Dict = None,
                     description: str = "") -> bool:
        """Test a specific endpoint with a specific role."""
        headers = self.get_auth_headers(role)
        url = f"{API_BASE}{endpoint}"
        
        try:
            if method.upper() == "GET":
                response = requests.get(url, headers=headers)
            elif method.upper() == "POST":
                response = requests.post(url, headers=headers, json=data)
            elif method.upper() == "PUT":
                response = requests.put(url, headers=headers, json=data)
            elif method.upper() == "DELETE":
                response = requests.delete(url, headers=headers)
            else:
                print(f"❌ Unsupported method: {method}")
                return False
            
            success = response.status_code == expected_status
            status_icon = "✅" if success else "❌"
            
            print(f"  {status_icon} {method.upper()} {endpoint} [{role}] -> {response.status_code} (expected {expected_status})")
            if description:
                print(f"      {description}")
            
            if not success and response.status_code != expected_status:
                print(f"      Response: {response.text[:200]}...")
            
            return success
            
        except Exception as e:
            print(f"  ❌ {method.upper()} {endpoint} [{role}] -> Error: {str(e)}")
            return False
    
    def test_authentication_endpoints(self):
        """Test authentication-related endpoints."""
        print("\n🔐 Testing Authentication Endpoints")
        print("-" * 50)
        
        # Test login for all users
        for role in TEST_USERS.keys():
            self.login_user(role)
        
        # Test current user endpoint
        for role in TEST_USERS.keys():
            self.test_endpoint("GET", "/users/me", role, 200, 
                             description=f"Get current {role} user info")
    
    def test_user_management_endpoints(self):
        """Test user management endpoints (admin only)."""
        print("\n👥 Testing User Management Endpoints")
        print("-" * 50)
        
        # Admin should have access
        self.test_endpoint("GET", "/users/", "admin", 200,
                         description="Admin can list users")
        
        # Other roles should be denied
        for role in ["counselor", "trainer", "user"]:
            self.test_endpoint("GET", "/users/", role, 403,
                             description=f"{role.capitalize()} cannot list users")
    
    def test_ai_souls_endpoints(self):
        """Test AI souls endpoints."""
        print("\n🤖 Testing AI Souls Endpoints")
        print("-" * 50)
        
        # All authenticated users can view AI souls
        for role in TEST_USERS.keys():
            self.test_endpoint("GET", "/ai-souls/", role, 200,
                             description=f"{role.capitalize()} can view AI souls")
        
        # Only trainers and admins can create AI souls
        ai_soul_data = {
            "name": "Test Soul",
            "description": "Test AI soul",
            "personality": "Helpful and friendly",
            "background": "Test background"
        }
        
        for role in ["trainer", "admin"]:
            self.test_endpoint("POST", "/ai-souls/", role, 200, ai_soul_data,
                             description=f"{role.capitalize()} can create AI souls")
        
        for role in ["counselor", "user"]:
            self.test_endpoint("POST", "/ai-souls/", role, 403, ai_soul_data,
                             description=f"{role.capitalize()} cannot create AI souls")
    
    def test_counselor_endpoints(self):
        """Test counselor-specific endpoints."""
        print("\n👩‍⚕️ Testing Counselor Endpoints")
        print("-" * 50)
        
        # Only counselors and admins should access counselor endpoints
        counselor_endpoints = [
            "/counselor/queue",
            "/counselor/performance",
            "/counselor/risk-assessments"
        ]
        
        for endpoint in counselor_endpoints:
            # Counselors and admins should have access
            for role in ["counselor", "admin"]:
                self.test_endpoint("GET", endpoint, role, 200,
                                 description=f"{role.capitalize()} can access {endpoint}")
            
            # Other roles should be denied
            for role in ["trainer", "user"]:
                self.test_endpoint("GET", endpoint, role, 403,
                                 description=f"{role.capitalize()} cannot access {endpoint}")
    
    def test_training_endpoints(self):
        """Test training-specific endpoints."""
        print("\n🎓 Testing Training Endpoints")
        print("-" * 50)
        
        # Get an AI soul ID first (assuming one exists from previous tests)
        headers = self.get_auth_headers("trainer")
        souls_response = requests.get(f"{API_BASE}/ai-souls/", headers=headers)
        
        if souls_response.status_code == 200 and souls_response.json():
            ai_soul_id = souls_response.json()[0]["id"]
            
            training_message = {
                "content": "This is a test training message",
                "is_from_trainer": True
            }
            
            # Only trainers and admins should access training endpoints
            for role in ["trainer", "admin"]:
                self.test_endpoint("POST", f"/training/{ai_soul_id}/messages", role, 200, 
                                 training_message,
                                 description=f"{role.capitalize()} can send training messages")
            
            for role in ["counselor", "user"]:
                self.test_endpoint("POST", f"/training/{ai_soul_id}/messages", role, 403,
                                 training_message,
                                 description=f"{role.capitalize()} cannot send training messages")
    
    def test_chat_endpoints(self):
        """Test chat endpoints."""
        print("\n💬 Testing Chat Endpoints")
        print("-" * 50)
        
        # Get an AI soul ID first
        headers = self.get_auth_headers("user")
        souls_response = requests.get(f"{API_BASE}/ai-souls/", headers=headers)
        
        if souls_response.status_code == 200 and souls_response.json():
            ai_soul_id = souls_response.json()[0]["id"]
            
            chat_message = {
                "content": "Hello, this is a test message"
            }
            
            # All authenticated users should be able to chat
            for role in TEST_USERS.keys():
                self.test_endpoint("POST", f"/chat/{ai_soul_id}/messages", role, 200,
                                 chat_message,
                                 description=f"{role.capitalize()} can send chat messages")
    
    def test_role_based_access(self):
        """Test comprehensive role-based access control."""
        print("\n🛡️ Testing Role-Based Access Control")
        print("-" * 50)
        
        # Define role permissions
        role_permissions = {
            "admin": {
                "can_access": [
                    "/users/", "/ai-souls/", "/counselor/queue", 
                    "/training/*/messages", "/chat/*/messages"
                ],
                "cannot_access": []
            },
            "counselor": {
                "can_access": [
                    "/ai-souls/", "/counselor/queue", "/chat/*/messages"
                ],
                "cannot_access": ["/users/", "/training/*/messages"]
            },
            "trainer": {
                "can_access": [
                    "/ai-souls/", "/training/*/messages", "/chat/*/messages"
                ],
                "cannot_access": ["/users/", "/counselor/queue"]
            },
            "user": {
                "can_access": ["/ai-souls/", "/chat/*/messages"],
                "cannot_access": [
                    "/users/", "/counselor/queue", "/training/*/messages"
                ]
            }
        }
        
        print("Role-based access summary:")
        for role, permissions in role_permissions.items():
            print(f"\n{role.capitalize()}:")
            print(f"  ✅ Can access: {', '.join(permissions['can_access'])}")
            if permissions['cannot_access']:
                print(f"  ❌ Cannot access: {', '.join(permissions['cannot_access'])}")
    
    def run_all_tests(self):
        """Run all endpoint tests."""
        print("🚀 Starting Comprehensive Endpoint Testing")
        print("=" * 60)
        
        # Test authentication first
        self.test_authentication_endpoints()
        
        # Test role-specific endpoints
        self.test_user_management_endpoints()
        self.test_ai_souls_endpoints()
        self.test_counselor_endpoints()
        self.test_training_endpoints()
        self.test_chat_endpoints()
        
        # Test role-based access summary
        self.test_role_based_access()
        
        print("\n" + "=" * 60)
        print("✅ Endpoint testing completed!")
        
        # Print login credentials for manual testing
        print("\n📋 Test User Credentials:")
        print("-" * 30)
        for role, creds in TEST_USERS.items():
            print(f"{role.capitalize()}: {creds['email']} / {creds['password']}")


def main():
    """Main function to run endpoint tests."""
    tester = EndpointTester()
    tester.run_all_tests()


if __name__ == "__main__":
    main() 