#!/usr/bin/env python3
"""
Test script for authentication endpoints.
This script tests the login, registration, and user profile endpoints.
"""

import requests
import json

# Configuration
BASE_URL = "http://localhost:8000"
AUTH_URL = f"{BASE_URL}/api/auth"

def test_health_check():
    """Test the health check endpoint"""
    try:
        response = requests.get(f"{BASE_URL}/health")
        print(f"✅ Health check: {response.status_code}")
        print(f"   Response: {response.json()}")
        return True
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return False

def test_signup():
    """Test user registration"""
    user_data = {
        "email": "test@example.com",
        "password": "testpassword123",
        "full_name": "Test User",
        "phone": "+1234567890"
    }
    
    try:
        response = requests.post(f"{AUTH_URL}/signup", json=user_data)
        print(f"✅ Signup: {response.status_code}")
        if response.status_code == 200:
            print(f"   User created: {response.json()}")
        else:
            print(f"   Error: {response.text}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Signup failed: {e}")
        return False

def test_login():
    """Test user login"""
    login_data = {
        "username": "test@example.com",
        "password": "testpassword123"
    }
    
    try:
        response = requests.post(f"{AUTH_URL}/login", data=login_data)
        print(f"✅ Login: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   Token received: {data['access_token'][:50]}...")
            return data['access_token']
        else:
            print(f"   Error: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Login failed: {e}")
        return None

def test_get_me(token):
    """Test getting current user profile"""
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.get(f"{AUTH_URL}/me", headers=headers)
        print(f"✅ Get profile: {response.status_code}")
        if response.status_code == 200:
            print(f"   User profile: {response.json()}")
            return True
        else:
            print(f"   Error: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Get profile failed: {e}")
        return False

def test_check_auth(token):
    """Test authentication check"""
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.get(f"{AUTH_URL}/check-auth", headers=headers)
        print(f"✅ Check auth: {response.status_code}")
        if response.status_code == 200:
            print(f"   Auth status: {response.json()}")
            return True
        else:
            print(f"   Error: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Check auth failed: {e}")
        return False

def test_logout(token):
    """Test logout"""
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.post(f"{AUTH_URL}/logout", headers=headers)
        print(f"✅ Logout: {response.status_code}")
        if response.status_code == 200:
            print(f"   Logout successful: {response.json()}")
            return True
        else:
            print(f"   Error: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Logout failed: {e}")
        return False

def main():
    """Run all authentication tests"""
    print("🧪 Testing Brahmavastu Authentication Endpoints")
    print("=" * 50)
    
    # Test health check
    if not test_health_check():
        print("❌ Health check failed. Make sure the server is running!")
        return
    
    print("\n" + "=" * 50)
    
    # Test signup
    signup_success = test_signup()
    
    print("\n" + "=" * 50)
    
    # Test login
    token = test_login()
    if not token:
        print("❌ Login failed. Cannot continue with other tests.")
        return
    
    print("\n" + "=" * 50)
    
    # Test get profile
    test_get_me(token)
    
    print("\n" + "=" * 50)
    
    # Test check auth
    test_check_auth(token)
    
    print("\n" + "=" * 50)
    
    # Test logout
    test_logout(token)
    
    print("\n" + "=" * 50)
    print("🎉 Authentication tests completed!")
    print("\n📝 Next steps:")
    print("1. Start your frontend application")
    print("2. Use the endpoints documented in FRONTEND_INTEGRATION.md")
    print("3. Test the login flow in your frontend")

if __name__ == "__main__":
    main() 