#!/usr/bin/env python3
"""
Test script for multiple file upload functionality
Tests the updated blog API endpoints with multiple files
"""

import requests
import os
from pathlib import Path

# API base URL
BASE_URL = "http://localhost:8000/api/blog"

def create_test_files():
    """Create test files for upload"""
    test_dir = Path("test_files")
    test_dir.mkdir(exist_ok=True)
    
    # Create test image files
    test_images = []
    for i in range(3):
        img_path = test_dir / f"test_image_{i+1}.png"
        with open(img_path, "wb") as f:
            # Create a simple 1x1 PNG file
            f.write(b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\tpHYs\x00\x00\x0b\x13\x00\x00\x0b\x13\x01\x00\x9a\x9c\x18\x00\x00\x00\nIDATx\x9cc```\x00\x00\x00\x04\x00\x01\xf5\x8e\xa4\x1c\x00\x00\x00\x00IEND\xaeB`\x82')
        test_images.append(str(img_path))
    
    # Create test PDF files
    test_pdfs = []
    for i in range(2):
        pdf_path = test_dir / f"test_pdf_{i+1}.pdf"
        with open(pdf_path, "wb") as f:
            # Create a minimal PDF file
            f.write(b'%PDF-1.4\n1 0 obj\n<<\n/Type /Catalog\n/Pages 2 0 R\n>>\nendobj\n2 0 obj\n<<\n/Type /Pages\n/Kids [3 0 R]\n/Count 1\n>>\nendobj\n3 0 obj\n<<\n/Type /Page\n/Parent 2 0 R\n/MediaBox [0 0 612 792]\n>>\nendobj\nxref\n0 4\n0000000000 65535 f \n0000000009 00000 n \n0000000058 00000 n \n0000000115 00000 n \ntrailer\n<<\n/Size 4\n/Root 1 0 R\n>>\nstartxref\n174\n%%EOF')
        test_pdfs.append(str(pdf_path))
    
    return test_images, test_pdfs

def test_books_multiple_files():
    """Test books endpoint with multiple files"""
    print("Testing books endpoint with multiple files...")
    
    test_images, test_pdfs = create_test_files()
    
    # Prepare form data
    data = {
        'title': 'Test Book with Multiple Files',
        'author': 'Test Author',
        'summary': 'This is a test book with multiple files',
        'rating': '4.5',
        'pages': '200',
        'price': '29.99',
        'publication_year': '2024',
        'publisher': 'Test Publisher',
        'category': 'Technology',
        'isbn': '978-0-123456-78-9'
    }
    
    # Prepare files
    files = []
    
    # Add multiple images
    for img_path in test_images:
        files.append(('images', (os.path.basename(img_path), open(img_path, 'rb'), 'image/png')))
    
    # Add multiple PDFs
    for pdf_path in test_pdfs:
        files.append(('pdfs', (os.path.basename(pdf_path), open(pdf_path, 'rb'), 'application/pdf')))
    
    try:
        response = requests.post(f"{BASE_URL}/books", data=data, files=files)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
        
        if response.status_code == 200:
            print("✅ Books endpoint with multiple files: SUCCESS")
        else:
            print("❌ Books endpoint with multiple files: FAILED")
            
    except Exception as e:
        print(f"❌ Error testing books endpoint: {str(e)}")
    finally:
        # Close files
        for _, (_, file_obj, _) in files:
            file_obj.close()

def test_tips_multiple_files():
    """Test tips endpoint with multiple files"""
    print("\nTesting tips endpoint with multiple files...")
    
    test_images, _ = create_test_files()
    
    # Prepare form data
    data = {
        'title': 'Test Tip with Multiple Images',
        'content': 'This is a test tip with multiple images',
        'category': 'general',
        'descriptions': ['Description 1', 'Description 2', 'Description 3']
    }
    
    # Prepare files
    files = []
    
    # Add multiple images
    for img_path in test_images:
        files.append(('images', (os.path.basename(img_path), open(img_path, 'rb'), 'image/png')))
    
    try:
        response = requests.post(f"{BASE_URL}/tips", data=data, files=files)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
        
        if response.status_code == 200:
            print("✅ Tips endpoint with multiple files: SUCCESS")
        else:
            print("❌ Tips endpoint with multiple files: FAILED")
            
    except Exception as e:
        print(f"❌ Error testing tips endpoint: {str(e)}")
    finally:
        # Close files
        for _, (_, file_obj, _) in files:
            file_obj.close()

def test_backward_compatibility():
    """Test backward compatibility with single files"""
    print("\nTesting backward compatibility with single files...")
    
    test_images, test_pdfs = create_test_files()
    
    # Test books with single file (backward compatibility)
    data = {
        'title': 'Test Book Single File',
        'author': 'Test Author',
        'summary': 'This is a test book with single file',
        'rating': '4.0',
        'pages': '150',
        'price': '19.99'
    }
    
    files = [
        ('pdf', (os.path.basename(test_pdfs[0]), open(test_pdfs[0], 'rb'), 'application/pdf'))
    ]
    
    try:
        response = requests.post(f"{BASE_URL}/books", data=data, files=files)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
        
        if response.status_code == 200:
            print("✅ Books endpoint backward compatibility: SUCCESS")
        else:
            print("❌ Books endpoint backward compatibility: FAILED")
            
    except Exception as e:
        print(f"❌ Error testing backward compatibility: {str(e)}")
    finally:
        # Close files
        for _, (_, file_obj, _) in files:
            file_obj.close()

def cleanup_test_files():
    """Clean up test files"""
    import shutil
    test_dir = Path("test_files")
    if test_dir.exists():
        shutil.rmtree(test_dir)
        print("\n🧹 Cleaned up test files")

if __name__ == "__main__":
    print("🚀 Testing Multiple File Upload Functionality")
    print("=" * 50)
    
    try:
        # Test multiple files
        test_books_multiple_files()
        test_tips_multiple_files()
        test_backward_compatibility()
        
        print("\n" + "=" * 50)
        print("✅ All tests completed!")
        
    except Exception as e:
        print(f"\n❌ Test suite failed: {str(e)}")
    
    finally:
        cleanup_test_files()
