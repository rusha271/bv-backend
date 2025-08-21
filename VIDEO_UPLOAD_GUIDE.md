# Video Upload Guide for MySQL Backend

This guide explains how to upload video data to your MySQL database using the FastAPI backend.

## Overview

The video upload system includes:
- **File Storage**: Videos are stored in the file system (`app/static/videos/`)
- **Database Records**: Video metadata is stored in MySQL tables
- **Thumbnail Generation**: Automatic thumbnail creation from video frames
- **Duration Detection**: Automatic video duration extraction
- **View Tracking**: View count tracking for videos

## Database Schema

### Video Table
```sql
CREATE TABLE videos (
    id INT PRIMARY KEY AUTO_INCREMENT,
    title VARCHAR(255) NOT NULL,
    description TEXT NOT NULL,
    url VARCHAR(500) NOT NULL,
    video_type VARCHAR(50) DEFAULT 'youtube',
    youtube_id VARCHAR(50),
    thumbnail_url VARCHAR(500),
    duration VARCHAR(20),
    views INT DEFAULT 0,
    category VARCHAR(100),
    is_published BOOLEAN DEFAULT TRUE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);
```

### MediaAsset Table
```sql
CREATE TABLE media_assets (
    id INT PRIMARY KEY AUTO_INCREMENT,
    filename VARCHAR(255) NOT NULL,
    original_name VARCHAR(255) NOT NULL,
    file_path VARCHAR(500) NOT NULL,
    file_size INT NOT NULL,
    mime_type VARCHAR(100) NOT NULL,
    asset_type VARCHAR(50) NOT NULL,
    content_type VARCHAR(50),
    content_id INT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);
```

## API Endpoints

### 1. Upload Video
```http
POST /api/videos/upload
Content-Type: multipart/form-data
Authorization: Bearer <token>

Form Data:
- file: Video file (MP4, AVI, MOV, WMV, FLV, WebM, MKV)
- title: Video title
- description: Video description
- category: Video category (optional)
```

**Response:**
```json
{
    "id": 1,
    "title": "Vastu Tips for Home",
    "description": "Complete guide to Vastu principles",
    "url": "/static/videos/uuid_filename.mp4",
    "video_type": "direct",
    "thumbnail_url": "/static/thumbnails/uuid_thumbnail.jpg",
    "duration": "15:30",
    "views": 0,
    "category": "vastu_tips",
    "is_published": true,
    "created_at": "2024-01-01T10:00:00",
    "updated_at": "2024-01-01T10:00:00"
}
```

### 2. Get All Videos
```http
GET /api/videos/
Query Parameters:
- skip: Number of videos to skip (pagination)
- limit: Maximum number of videos to return
- category: Filter by category
```

### 3. Get Specific Video
```http
GET /api/videos/{video_id}
```

### 4. Update Video
```http
PUT /api/videos/{video_id}
Authorization: Bearer <token>
Content-Type: application/json

{
    "title": "Updated Title",
    "description": "Updated description",
    "category": "new_category"
}
```

### 5. Delete Video (Soft Delete)
```http
DELETE /api/videos/{video_id}
Authorization: Bearer <token>
```

### 6. Increment Views
```http
POST /api/videos/{video_id}/increment-views
```

### 7. Serve Video File
```http
GET /api/videos/serve/{filename}
```

### 8. Serve Thumbnail
```http
GET /api/videos/thumbnails/{filename}
```

## Usage Examples

### Python Requests Example

```python
import requests

# Login to get token
login_data = {
    "email": "user@example.com",
    "password": "password123"
}
response = requests.post("http://localhost:8000/api/auth/login", json=login_data)
token = response.json()["access_token"]

# Upload video
headers = {"Authorization": f"Bearer {token}"}
with open("video.mp4", "rb") as video_file:
    files = {"file": ("video.mp4", video_file, "video/mp4")}
    data = {
        "title": "My Video",
        "description": "Video description",
        "category": "tutorial"
    }
    response = requests.post(
        "http://localhost:8000/api/videos/upload",
        headers=headers,
        data=data,
        files=files
    )
    video = response.json()
    print(f"Video uploaded: {video['title']}")
```

### JavaScript/Fetch Example

```javascript
// Upload video
async function uploadVideo(file, title, description, category) {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('title', title);
    formData.append('description', description);
    formData.append('category', category);

    const response = await fetch('http://localhost:8000/api/videos/upload', {
        method: 'POST',
        headers: {
            'Authorization': `Bearer ${token}`
        },
        body: formData
    });

    return await response.json();
}

// Get all videos
async function getVideos() {
    const response = await fetch('http://localhost:8000/api/videos/');
    return await response.json();
}
```

### cURL Example

```bash
# Upload video
curl -X POST "http://localhost:8000/api/videos/upload" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "file=@video.mp4" \
  -F "title=My Video" \
  -F "description=Video description" \
  -F "category=tutorial"

# Get videos
curl "http://localhost:8000/api/videos/"

# Get specific video
curl "http://localhost:8000/api/videos/1"
```

## File Storage Structure

```
app/
├── static/
│   ├── videos/           # Video files
│   │   ├── uuid1.mp4
│   │   ├── uuid2.avi
│   │   └── ...
│   └── thumbnails/       # Video thumbnails
│       ├── uuid1.jpg
│       ├── uuid2.jpg
│       └── ...
```

## Configuration

### File Size Limits
- **Maximum Video Size**: 500MB (configurable in `app/utils/helpers.py`)
- **Maximum Image Size**: 10MB

### Supported Video Formats
- MP4 (.mp4)
- AVI (.avi)
- MOV (.mov)
- WMV (.wmv)
- FLV (.flv)
- WebM (.webm)
- MKV (.mkv)

### Environment Variables
Add these to your `.env` file:
```env
# Video upload settings
MAX_VIDEO_SIZE_MB=500
UPLOAD_DIR=app/static/videos
THUMBNAIL_DIR=app/static/thumbnails
```

## Dependencies

### Required Python Packages
```bash
pip install fastapi python-multipart
```

### Optional: FFmpeg for Advanced Features
For thumbnail generation and duration detection:
```bash
# Ubuntu/Debian
sudo apt-get install ffmpeg

# macOS
brew install ffmpeg

# Windows
# Download from https://ffmpeg.org/download.html
```

## Security Considerations

1. **File Validation**: All uploaded files are validated for type and size
2. **Authentication**: Upload endpoints require valid JWT tokens
3. **File Isolation**: Files are stored with unique UUIDs to prevent conflicts
4. **Content Type Validation**: Only allowed video formats are accepted
5. **Path Traversal Protection**: File paths are sanitized

## Error Handling

Common error responses:

```json
{
    "detail": "Invalid video file type. Allowed types: MP4, AVI, MOV, WMV, FLV, WebM, MKV"
}
```

```json
{
    "detail": "Video file too large (max 500MB)."
}
```

```json
{
    "detail": "Invalid video file extension."
}
```

## Performance Tips

1. **Large Files**: For videos > 100MB, consider using chunked uploads
2. **CDN**: For production, serve videos through a CDN
3. **Compression**: Consider video compression before upload
4. **Thumbnails**: Generate thumbnails asynchronously for better performance

## Testing

Run the test script:
```bash
python test_video_upload.py
```

## Troubleshooting

### Common Issues

1. **File Upload Fails**
   - Check file size limits
   - Verify file format is supported
   - Ensure proper authentication

2. **Thumbnail Generation Fails**
   - Install FFmpeg
   - Check file permissions
   - Verify video file is not corrupted

3. **Database Errors**
   - Check MySQL connection
   - Verify table schema
   - Check for foreign key constraints

4. **Permission Errors**
   - Ensure upload directories exist
   - Check file system permissions
   - Verify application has write access

## Production Considerations

1. **Storage**: Use cloud storage (AWS S3, Google Cloud Storage) for production
2. **CDN**: Implement CDN for video delivery
3. **Monitoring**: Add logging for upload failures
4. **Backup**: Implement backup strategy for video files
5. **Cleanup**: Implement cleanup for unused files 