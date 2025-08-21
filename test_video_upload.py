#!/usr/bin/env python3
"""
Test script for video upload functionality
This script demonstrates how to upload videos to the MySQL database
"""

import requests
import json
import os
from pathlib import Path

# Configuration
BASE_URL = "http://localhost:8000"
API_BASE = f"{BASE_URL}/api"

def login_and_get_token(email: str, password: str) -> str:
    """Login and get JWT token"""
    login_data = {
        "email": email,
        "password": password
    }
    
    response = requests.post(f"{API_BASE}/auth/login", json=login_data)
    if response.status_code == 200:
        return response.json()["access_token"]
    else:
        raise Exception(f"Login failed: {response.text}")

def upload_video(token: str, video_path: str, title: str, description: str, category: str = None):
    """Upload a video file"""
    headers = {
        "Authorization": f"Bearer {token}"
    }
    
    # Prepare form data
    data = {
        "title": title,
        "description": description
    }
    if category:
        data["category"] = category
    
    # Prepare file
    with open(video_path, "rb") as video_file:
        files = {
            "file": (os.path.basename(video_path), video_file, "video/mp4")
        }
        
        response = requests.post(
            f"{API_BASE}/videos/upload",
            headers=headers,
            data=data,
            files=files
        )
    
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Upload failed: {response.text}")

def get_videos(token: str = None):
    """Get all videos"""
    headers = {}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    
    response = requests.get(f"{API_BASE}/videos/", headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Failed to get videos: {response.text}")

def get_video(video_id: int, token: str = None):
    """Get a specific video"""
    headers = {}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    
    response = requests.get(f"{API_BASE}/videos/{video_id}", headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Failed to get video: {response.text}")

def update_video(video_id: int, token: str, **updates):
    """Update video information"""
    headers = {
        "Authorization": f"Bearer {token}"
    }
    
    response = requests.put(
        f"{API_BASE}/videos/{video_id}",
        headers=headers,
        json=updates
    )
    
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Update failed: {response.text}")

def increment_views(video_id: int):
    """Increment video view count"""
    response = requests.post(f"{API_BASE}/videos/{video_id}/increment-views")
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Failed to increment views: {response.text}")

def main():
    """Main test function"""
    print("=== Video Upload Test Script ===\n")
    
    # Test credentials (replace with actual user credentials)
    email = "admin@example.com"  # Replace with actual email
    password = "admin123"        # Replace with actual password
    
    try:
        # 1. Login and get token
        print("1. Logging in...")
        token = login_and_get_token(email, password)
        print(f"✅ Login successful. Token: {token[:50]}...")
        
        # 2. Get existing videos
        print("\n2. Getting existing videos...")
        videos = get_videos()
        print(f"✅ Found {len(videos)} existing videos")
        
        # 3. Upload a test video (if you have a video file)
        # Uncomment and modify the path to test with an actual video file
        """
        video_path = "path/to/your/test/video.mp4"  # Replace with actual video path
        if os.path.exists(video_path):
            print("\n3. Uploading test video...")
            uploaded_video = upload_video(
                token=token,
                video_path=video_path,
                title="Test Vastu Video",
                description="This is a test video for Vastu consultation",
                category="vastu_tips"
            )
            print(f"✅ Video uploaded successfully: {uploaded_video['title']}")
            video_id = uploaded_video['id']
        else:
            print("\n3. Skipping video upload (no test video file found)")
            video_id = 1  # Use existing video ID for testing
        """
        
        # For testing without actual video file, use existing video
        video_id = 1
        print(f"\n3. Using existing video ID: {video_id}")
        
        # 4. Get specific video
        print(f"\n4. Getting video {video_id}...")
        video = get_video(video_id)
        print(f"✅ Video details: {video['title']}")
        
        # 5. Update video
        print(f"\n5. Updating video {video_id}...")
        updated_video = update_video(
            video_id=video_id,
            token=token,
            description="Updated description for testing"
        )
        print(f"✅ Video updated: {updated_video['description']}")
        
        # 6. Increment views
        print(f"\n6. Incrementing views for video {video_id}...")
        views_result = increment_views(video_id)
        print(f"✅ Views incremented: {views_result['views']}")
        
        # 7. Get all videos again
        print("\n7. Getting all videos after updates...")
        final_videos = get_videos()
        print(f"✅ Total videos: {len(final_videos)}")
        
        print("\n=== Test completed successfully! ===")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    main() 