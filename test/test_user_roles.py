#!/usr/bin/env python3
"""
Test script to check user roles in the AI Soul Entity system
"""

import requests
import json

# API base URL
BASE_URL = "http://localhost:8000/api/v1"

def login_admin():
    """Login as admin to get access token"""
    login_data = {
        "grant_type": "password",
        "username": "admin@example.com",  # Default admin email
        "password": "changethis",  # Default admin password
        "scope": "",
        "client_id": "",
        "client_secret": ""
    }
    
    response = requests.post(f"{BASE_URL}/login/access-token", data=login_data)
    if response.status_code == 200:
        return response.json()["access_token"]
    else:
        print(f"Login failed: {response.status_code} - {response.text}")
        return None

def get_users(token):
    """Get all users"""
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/users/?skip=0&limit=50", headers=headers)
    
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Failed to get users: {response.status_code} - {response.text}")
        return None

def main():
    print("Testing user roles...")
    
    # Login as admin
    token = login_admin()
    if not token:
        print("Failed to login as admin")
        return
    
    print("✅ Admin login successful")
    
    # Get users
    users_data = get_users(token)
    if not users_data:
        print("Failed to get users")
        return
    
    print(f"✅ Found {users_data['count']} users total")
    print(f"✅ Showing {len(users_data['data'])} users in this page")
    
    # Check specific users
    print("\n📋 User Roles:")
    print("-" * 50)
    
    for user in users_data['data']:
        role = user.get('role', 'unknown')
        is_superuser = user.get('is_superuser', False)
        display_role = "Administrator" if is_superuser else role.capitalize()
        
        print(f"👤 {user['full_name'] or 'N/A'} ({user['email']})")
        print(f"   Role: {display_role}")
        print(f"   Active: {'Yes' if user.get('is_active', False) else 'No'}")
        print()
    
    # Look for Tim specifically
    tim_user = None
    for user in users_data['data']:
        if user['email'] == 'aura@gmail.com':
            tim_user = user
            break
    
    if tim_user:
        print("🎯 Found Tim (aura@gmail.com):")
        print(f"   Full Name: {tim_user['full_name'] or 'N/A'}")
        print(f"   Role: {tim_user.get('role', 'unknown')}")
        print(f"   Is Superuser: {tim_user.get('is_superuser', False)}")
        print(f"   Active: {'Yes' if tim_user.get('is_active', False) else 'No'}")
        
        expected_role = "trainer"
        actual_role = tim_user.get('role', '').lower()
        if actual_role == expected_role:
            print("✅ Tim's role is correctly set as trainer")
        else:
            print(f"❌ Tim's role is '{actual_role}', expected '{expected_role}'")
    else:
        print("❌ Tim (aura@gmail.com) not found in users list")

if __name__ == "__main__":
    main() 