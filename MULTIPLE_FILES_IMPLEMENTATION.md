# Multiple Files Support Implementation

## 🎯 Overview
This document outlines the implementation of multiple file upload support for the UnifiedPostCreator component in the backend API.

## ✅ Changes Made

### 1. Database Models Updated (`app/models/blog.py`)
- **VastuTip**: Added `image_urls` (JSON) and `descriptions` (JSON) fields
- **Book**: Added `image_urls` (JSON) and `pdf_urls` (JSON) fields  
- **Video**: Added `video_urls` (JSON) and `thumbnail_urls` (JSON) fields
- **Backward Compatibility**: Kept original single file fields (`image_url`, `pdf_url`, etc.)

### 2. Schemas Updated
- **`app/schemas/blog.py`**: Updated Book and Video schemas with multiple file support
- **`app/schemas/vastu.py`**: Updated VastuTip schemas with multiple file support
- All schemas maintain backward compatibility with single file fields

### 3. File Handling Utility (`app/utils/file_handler.py`)
- **MultipleFileHandler**: New class for handling multiple file uploads
- **Unique Naming**: Generates unique filenames with UUIDs
- **Content-Specific Folders**: Organizes files by content type and ID
- **File Validation**: Validates file types, sizes, and quantities
- **Error Handling**: Comprehensive error handling with cleanup

### 4. API Endpoints Updated (`app/api/blog.py`)

#### Books Endpoint (`POST /api/blog/books`)
- **New Parameters**: `pdfs[]`, `images[]` for multiple files
- **Backward Compatibility**: Still accepts single `pdf` parameter
- **Response**: Returns both single URLs and arrays of URLs

#### Tips Endpoint (`POST /api/blog/tips`)
- **New Parameters**: `images[]`, `descriptions[]` for multiple files/descriptions
- **Backward Compatibility**: Still accepts single `image` parameter
- **Response**: Returns both single image and array of images

#### Videos Endpoint (`POST /api/blog/videos`)
- **New Parameters**: `videos[]`, `thumbnails[]` for multiple files
- **Backward Compatibility**: Still accepts single `video` and `thumbnail` parameters
- **Response**: Returns both single URLs and arrays of URLs

### 5. Database Migration
- **Migration Applied**: `dfdb7a0e6c7c_add_multiple_files_support_safe`
- **New Columns**: Added JSON columns for multiple file URLs
- **Safe Migration**: Handles existing data without conflicts

## 🔧 File Type Configurations

### Images
- **Allowed Types**: JPEG, PNG, GIF, WebP
- **Max Size**: 5MB per file
- **Max Files**: 10 files

### Videos
- **Allowed Types**: MP4, AVI, MOV, WMV, WebM
- **Max Size**: 100MB per file
- **Max Files**: 5 files

### Documents (PDFs)
- **Allowed Types**: PDF, DOC, DOCX
- **Max Size**: 20MB per file
- **Max Files**: 10 files

### Audio
- **Allowed Types**: MP3, WAV, OGG
- **Max Size**: 50MB per file
- **Max Files**: 5 files

## 📁 File Organization

### Folder Structure
```
app/static/media/
├── books/
│   └── content_{book_id}/
│       ├── image_1_uuid.png
│       ├── image_2_uuid.png
│       └── pdf_1_uuid.pdf
├── videos/
│   └── content_{video_id}/
│       ├── video_1_uuid.mp4
│       └── thumbnail_1_uuid.png
└── tips/
    └── content_{tip_id}/
        └── image_1_uuid.png
```

## 🔄 Backward Compatibility

### Single File Support
- All endpoints still accept single file parameters
- Original response format maintained
- Existing clients continue to work

### Response Format
```json
{
  "id": 1,
  "title": "Example",
  "image_url": "/static/media/books/content_1/image_1.png",  // Single file (backward compatibility)
  "image_urls": [                                          // Multiple files (new)
    "/static/media/books/content_1/image_1.png",
    "/static/media/books/content_1/image_2.png"
  ],
  "pdf_url": "/static/media/books/content_1/pdf_1.pdf",     // Single file (backward compatibility)
  "pdf_urls": [                                            // Multiple files (new)
    "/static/media/books/content_1/pdf_1.pdf",
    "/static/media/books/content_1/pdf_2.pdf"
  ]
}
```

## 🧪 Testing

### Test Script
- **File**: `test_multiple_files_api.py`
- **Tests**: Multiple file uploads, backward compatibility
- **Coverage**: Books, Tips, Videos endpoints

### Manual Testing
```bash
# Test multiple files
curl -X POST "http://localhost:8000/api/blog/books" \
  -F "title=Test Book" \
  -F "author=Test Author" \
  -F "summary=Test Summary" \
  -F "images=@image1.png" \
  -F "images=@image2.png" \
  -F "pdfs=@doc1.pdf" \
  -F "pdfs=@doc2.pdf"

# Test backward compatibility
curl -X POST "http://localhost:8000/api/blog/books" \
  -F "title=Test Book" \
  -F "author=Test Author" \
  -F "summary=Test Summary" \
  -F "pdf=@document.pdf"
```

## 🚀 Usage Examples

### Frontend Integration
```javascript
// Multiple files
const formData = new FormData();
formData.append('title', 'My Book');
formData.append('author', 'Author Name');
formData.append('summary', 'Book summary');

// Add multiple images
files.images.forEach(file => {
  formData.append('images', file);
});

// Add multiple PDFs
files.pdfs.forEach(file => {
  formData.append('pdfs', file);
});

// Submit
fetch('/api/blog/books', {
  method: 'POST',
  body: formData
});
```

### Response Handling
```javascript
const response = await fetch('/api/blog/books', { method: 'POST', body: formData });
const data = await response.json();

// Access single file (backward compatibility)
console.log('Main image:', data.image_url);

// Access multiple files (new feature)
console.log('All images:', data.image_urls);
console.log('All PDFs:', data.pdf_urls);
```

## 🔒 Security Features

### File Validation
- **MIME Type Checking**: Validates actual file content
- **Size Limits**: Prevents oversized uploads
- **Quantity Limits**: Prevents abuse
- **Extension Validation**: Checks file extensions

### Error Handling
- **Graceful Failures**: Individual file failures don't break entire upload
- **Cleanup**: Failed uploads are cleaned up automatically
- **Detailed Errors**: Specific error messages for each file

## 📊 Performance Considerations

### File Storage
- **Unique Naming**: Prevents filename conflicts
- **Organized Structure**: Easy file management
- **Efficient Cleanup**: Failed uploads are cleaned up

### Database
- **JSON Storage**: Efficient storage of multiple URLs
- **Indexed Fields**: Fast queries on file URLs
- **Backward Compatibility**: No breaking changes

## 🎉 Benefits

1. **UnifiedPostCreator Support**: Frontend can now upload multiple files
2. **Backward Compatibility**: Existing functionality preserved
3. **Modular Design**: Easy to extend for new file types
4. **Error Resilience**: Robust error handling and cleanup
5. **Performance**: Efficient file organization and storage
6. **Security**: Comprehensive validation and security measures

## 🔧 Maintenance

### Adding New File Types
1. Update `FILE_TYPE_CONFIGS` in `file_handler.py`
2. Add new columns to database models
3. Update API endpoints to handle new file types
4. Update schemas with new fields

### Monitoring
- Monitor file storage usage
- Track upload success/failure rates
- Monitor API response times
- Check for storage cleanup issues

## ✅ Status: COMPLETE

All requirements have been implemented:
- ✅ Multiple file uploads for all content types
- ✅ Backward compatibility maintained
- ✅ Database schema updated
- ✅ API endpoints updated
- ✅ File validation and security
- ✅ Error handling and cleanup
- ✅ Testing framework ready
- ✅ Documentation complete
