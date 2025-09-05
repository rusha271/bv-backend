#!/usr/bin/env python3
"""
Test script for the updated book and video endpoints with new FormData payloads
"""

import requests
import json
import os
from pathlib import Path

# Configuration
BASE_URL = "http://localhost:8000"
API_BASE = f"{BASE_URL}/api/blog"

def login_and_get_token(email: str = "admin@example.com", password: str = "admin123") -> str:
    """Login and get access token"""
    login_data = {
        "email": email,
        "password": password
    }
    
    response = requests.post(f"{BASE_URL}/api/auth/login", json=login_data)
    
    if response.status_code == 200:
        return response.json()["access_token"]
    else:
        raise Exception(f"Login failed: {response.text}")

def test_book_upload(token: str):
    """Test book upload with new FormData payload structure"""
    print("Testing book upload...")
    
    # Create a dummy PDF file for testing
    test_pdf_path = "test_book.pdf"
    with open(test_pdf_path, "wb") as f:
        f.write(b"PDF content for testing")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # FormData payload matching your structure
    form_data = {
        "title": "Vastu Shastra for Modern Homes",
        "author": "Dr. Rajesh Kumar", 
        "summary": "A comprehensive guide to applying Vastu principles in modern architecture...",
        "rating": "4.5",
        "pages": "250",
        "price": "29.99",
        "publication_year": "2023",
        "publisher": "Vastu Publications",
        "category": "Vastu Tips",
        "isbn": "978-1234567890"
    }
    
    files = {
        "pdf": ("vastu_guide.pdf", open(test_pdf_path, "rb"), "application/pdf")
    }
    
    try:
        response = requests.post(
            f"{API_BASE}/books",
            data=form_data,
            files=files,
            headers=headers
        )
        
        print(f"Book upload status: {response.status_code}")
        if response.status_code == 200:
            book_data = response.json()
            print(f"Book created successfully: {book_data['title']}")
            print(f"Book ID: {book_data['id']}")
            print(f"PDF URL: {book_data['image_url']}")
        else:
            print(f"Book upload failed: {response.text}")
            
    except Exception as e:
        print(f"Book upload error: {str(e)}")
    finally:
        files["pdf"][1].close()
        if os.path.exists(test_pdf_path):
            os.remove(test_pdf_path)

def test_video_upload(token: str):
    """Test video upload with new FormData payload structure"""
    print("\nTesting video upload...")
    
    # Create dummy files for testing
    test_video_path = "test_video.mp4"
    test_thumbnail_path = "test_thumbnail.png"
    
    with open(test_video_path, "wb") as f:
        f.write(b"Video content for testing")
    
    with open(test_thumbnail_path, "wb") as f:
        f.write(b"Thumbnail content for testing")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # FormData payload matching your structure
    form_data = {
        "title": "Vastu Tips for Kitchen Design",
        "description": "Learn essential Vastu principles for designing an auspicious kitchen...",
        "category": "Tutorial"
    }
    
    files = {
        "video": ("kitchen_vastu.mp4", open(test_video_path, "rb"), "video/mp4"),
        "thumbnail": ("thumbnail.png", open(test_thumbnail_path, "rb"), "image/png")
    }
    
    try:
        response = requests.post(
            f"{API_BASE}/videos",
            data=form_data,
            files=files,
            headers=headers
        )
        
        print(f"Video upload status: {response.status_code}")
        if response.status_code == 200:
            video_data = response.json()
            print(f"Video created successfully: {video_data['title']}")
            print(f"Video ID: {video_data['id']}")
            print(f"Video URL: {video_data.get('url', 'NOT SET')}")
            print(f"Thumbnail URL: {video_data['thumbnail_url']}")
            print(f"Duration: {video_data.get('duration', 'NOT SET')}")
            print(f"Category: {video_data.get('category', 'NOT SET')}")
        else:
            print(f"Video upload failed: {response.text}")
            
    except Exception as e:
        print(f"Video upload error: {str(e)}")
    finally:
        files["video"][1].close()
        files["thumbnail"][1].close()
        if os.path.exists(test_video_path):
            os.remove(test_video_path)
        if os.path.exists(test_thumbnail_path):
            os.remove(test_thumbnail_path)

def test_video_serving():
    """Test video serving endpoints"""
    print("\nTesting video serving endpoints...")
    
    try:
        # First get the list of videos to find a video filename
        response = requests.get(f"{API_BASE}/videos")
        if response.status_code == 200:
            videos = response.json()
            if videos:
                video = videos[0]
                video_url = video.get('url', '')
                if video_url:
                    # Extract filename from URL
                    filename = video_url.split('/')[-1]
                    print(f"Testing video serving for: {filename}")
                    
                    # Test video serving endpoint
                    response = requests.get(f"{API_BASE}/videos/serve/{filename}")
                    print(f"Video serving status: {response.status_code}")
                    if response.status_code == 200:
                        print(f"Video file size: {len(response.content)} bytes")
                        print(f"Content type: {response.headers.get('content-type', 'unknown')}")
                    else:
                        print(f"Video serving failed: {response.text}")
                
                # Test thumbnail serving
                thumbnail_url = video.get('thumbnail_url', '')
                if thumbnail_url:
                    thumb_filename = thumbnail_url.split('/')[-1]
                    print(f"Testing thumbnail serving for: {thumb_filename}")
                    
                    response = requests.get(f"{API_BASE}/videos/thumbnails/{thumb_filename}")
                    print(f"Thumbnail serving status: {response.status_code}")
                    if response.status_code == 200:
                        print(f"Thumbnail file size: {len(response.content)} bytes")
                        print(f"Content type: {response.headers.get('content-type', 'unknown')}")
                    else:
                        print(f"Thumbnail serving failed: {response.text}")
            else:
                print("No videos found to test serving")
        else:
            print(f"Failed to get videos list: {response.status_code}")
            
    except Exception as e:
        print(f"Video serving test error: {str(e)}")

def test_list_endpoints():
    """Test the list endpoints"""
    print("\nTesting list endpoints...")
    
    try:
        # Test books list
        response = requests.get(f"{API_BASE}/books")
        print(f"Books list status: {response.status_code}")
        if response.status_code == 200:
            books = response.json()
            print(f"Found {len(books)} books")
        
        # Test videos list
        response = requests.get(f"{API_BASE}/videos")
        print(f"Videos list status: {response.status_code}")
        if response.status_code == 200:
            videos = response.json()
            print(f"Found {len(videos)} videos")
            
            # Show detailed video information
            for i, video in enumerate(videos):
                print(f"  Video {i+1}:")
                print(f"    ID: {video.get('id')}")
                print(f"    Title: {video.get('title')}")
                print(f"    URL: {video.get('url', 'NULL')}")
                print(f"    Thumbnail: {video.get('thumbnail_url', 'NULL')}")
                print(f"    Duration: {video.get('duration', 'NULL')}")
                print()
            
    except Exception as e:
        print(f"List endpoints error: {str(e)}")

def main():
    """Main test function"""
    print("Testing updated book and video endpoints...")
    print("=" * 50)
    
    try:
        # Get authentication token
        token = login_and_get_token()
        print(f"Authentication successful")
        
        # Test endpoints
        test_book_upload(token)
        test_video_upload(token)
        test_list_endpoints()
        test_video_serving()
        
        print("\n" + "=" * 50)
        print("Testing completed!")
        
    except Exception as e:
        print(f"Test failed: {str(e)}")

if __name__ == "__main__":
    main()
