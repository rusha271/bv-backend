# File Management Guide

This guide explains how to manage files in the BV Backend system, including deletion and cleanup operations.

## File Deletion Features

### 1. Individual File Deletion

**Endpoint:** `DELETE /api/files/{file_id}`

Delete a specific file and all its associated data (floorplan analyses, etc.).

**Example:**
```bash
curl -X DELETE "http://localhost:8000/api/files/123" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Response:**
```json
{
  "message": "File deleted successfully"
}
```

### 2. List User Files

**Endpoint:** `GET /api/files/list/user`

List all files belonging to the current user.

**Example:**
```bash
curl "http://localhost:8000/api/files/list/user" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### 3. Cleanup Orphaned Files

**Endpoint:** `DELETE /api/files/cleanup/orphaned`

Remove files that exist on disk but are not referenced in the database.

**Example:**
```bash
curl -X DELETE "http://localhost:8000/api/files/cleanup/orphaned" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Response:**
```json
{
  "message": "Cleanup completed. Deleted 5 orphaned files.",
  "deleted_count": 5,
  "total_orphaned": 5
}
```

## Bulk Cleanup Script

Use the cleanup script for advanced file management operations.

### Installation

The script is located at: `app/scripts/cleanup_old_files.py`

### Usage

#### 1. View Storage Statistics

```bash
python app/scripts/cleanup_old_files.py --action stats
```

**Output:**
```
Storage Statistics:
Total files: 150
Total size: 245.67 MB

By file type:
  image/jpeg: 120 files, 180.50 MB
  image/png: 25 files, 45.20 MB
  application/pdf: 5 files, 19.97 MB
```

#### 2. Cleanup Old Files (Dry Run)

```bash
python app/scripts/cleanup_old_files.py --action cleanup-old --days 30
```

This shows what files would be deleted without actually deleting them.

#### 3. Cleanup Old Files (Execute)

```bash
python app/scripts/cleanup_old_files.py --action cleanup-old --days 30 --execute
```

This actually deletes files older than 30 days.

#### 4. Cleanup Orphaned Floorplan Data (Dry Run)

```bash
python app/scripts/cleanup_old_files.py --action cleanup-orphaned
```

#### 5. Cleanup Orphaned Floorplan Data (Execute)

```bash
python app/scripts/cleanup_old_files.py --action cleanup-orphaned --execute
```

## Database Schema Changes

### CASCADE Delete

The system now supports CASCADE delete, meaning:
- When you delete a file, all related floorplan analyses are automatically deleted
- No orphaned data is left in the database
- Physical files are also removed from disk

### Large File Support

- Image data is now stored as `LONGBLOB` instead of `BLOB`
- Supports files up to 4GB in size
- No more "Data too long for column" errors

## Best Practices

### 1. Regular Cleanup

Run cleanup operations regularly to manage storage:

```bash
# Weekly cleanup of files older than 30 days
python app/scripts/cleanup_old_files.py --action cleanup-old --days 30 --execute

# Monthly cleanup of orphaned data
python app/scripts/cleanup_old_files.py --action cleanup-orphaned --execute
```

### 2. Monitor Storage

Check storage usage regularly:

```bash
python app/scripts/cleanup_old_files.py --action stats
```

### 3. Backup Before Bulk Operations

Always backup your database before running bulk delete operations.

### 4. Test with Dry Run

Always use dry run first to see what will be deleted:

```bash
python app/scripts/cleanup_old_files.py --action cleanup-old --days 30
```

## Error Handling

The system includes comprehensive error handling:

- **Authorization**: Only file owners can delete their files
- **File Not Found**: Proper 404 responses for non-existent files
- **Database Rollback**: Automatic rollback on errors
- **Physical File Cleanup**: Handles cases where physical files are missing

## API Response Codes

- `200`: Success
- `403`: Not authorized to delete file
- `404`: File not found
- `500`: Server error during deletion

## Security Features

- User authentication required for all operations
- Users can only delete their own files
- CORS protection enabled
- Input validation and sanitization
