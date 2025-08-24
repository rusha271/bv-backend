#!/usr/bin/env python3
"""
Test script to verify the floorplan upload endpoint works correctly
"""
import requests
import json

# Test data
BASE_URL = "http://localhost:8000"

# Sample base64 image data (1x1 pixel JPEG)
sample_image_data = "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQABAAAD/2wBDAAYEBQYFBAYGBQYHBwYIChAKCgkJChQODwwQFxQYGBcUFhYaHSUfGhsjHBYWICwgIyYnKSopGR8tMC0oMCUoKSj/2wBDAQcHBwoIChMKChMoGhYaKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCj/wAARCAABAAEDASIAAhEBAxEB/8QAFQABAQAAAAAAAAAAAAAAAAAAAAv/xAAUEAEAAAAAAAAAAAAAAAAAAAAA/8QAFQEBAQAAAAAAAAAAAAAAAAAAAAX/xAAUEQEAAAAAAAAAAAAAAAAAAAAA/9oADAMBAAIRAxEAPwCdABmX/9k="

def test_upload_endpoint():
    """Test the floorplan upload endpoint"""
    print("Testing Floorplan Upload Endpoint")
    print("=" * 50)
    
    upload_data = {
        "image_data": sample_image_data,
        "image_format": "jpeg",
        "original_filename": "test.jpg"
    }
    
    url = f"{BASE_URL}/api/floorplan/upload"
    
    try:
        response = requests.post(url, headers={
            "Origin": "http://localhost:3000",
            "Content-Type": "application/json",
            "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMiIsInJvbGUiOiJndWVzdCIsImV4cCI6MTc1NjEyMDY3NX0.UofqdpzkPbbsyDcQ-vGa5tnHBFN7FAocPaKmTsb2wIU"
        }, json=upload_data)
        
        print(f"Status Code: {response.status_code}")
        print(f"Response Headers:")
        for header, value in response.headers.items():
            if "access-control" in header.lower():
                print(f"  {header}: {value}")
        
        if response.status_code == 200:
            print("✅ Upload successful!")
            response_data = response.json()
            print(f"Analysis ID: {response_data.get('id')}")
            print(f"Status: {response_data.get('status')}")
            print(f"Image data present: {'image_data' in response_data}")
        else:
            print("❌ Upload failed!")
            print(f"Error: {response.text}")
            
    except Exception as e:
        print(f"❌ Request failed: {str(e)}")

if __name__ == "__main__":
    test_upload_endpoint()
