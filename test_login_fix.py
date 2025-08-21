#!/usr/bin/env python3
"""
Test script to verify login endpoint fix
"""
import requests
import json

# Test configuration
BASE_URL = "http://localhost:8000"
LOGIN_URL = f"{BASE_URL}/api/auth/login"

def test_login():
    """Test the login endpoint"""
    print("Testing login endpoint...")
    
    # Test data
    login_data = {
        "email": "admin@gmail.com",
        "password": "admin123"
    }
    
    try:
        print(f"Sending POST request to {LOGIN_URL}")
        print(f"Request data: {json.dumps(login_data, indent=2)}")
        
        response = requests.post(LOGIN_URL, json=login_data)
        
        print(f"Response status code: {response.status_code}")
        print(f"Response headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Login successful!")
            print(f"Response data: {json.dumps(data, indent=2, default=str)}")
            
            # Check if user object has role field
            if 'user' in data and 'role' in data['user']:
                print("✅ User object contains role field")
                print(f"Role: {data['user']['role']}")
            else:
                print("❌ User object missing role field")
                print(f"User object keys: {list(data['user'].keys()) if 'user' in data else 'No user object'}")
        else:
            print(f"❌ Login failed with status {response.status_code}")
            print(f"Response text: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to server. Make sure the server is running on http://localhost:8000")
    except Exception as e:
        print(f"❌ Error occurred: {e}")

if __name__ == "__main__":
    test_login() 