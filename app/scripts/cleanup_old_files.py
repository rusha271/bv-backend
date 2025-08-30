#!/usr/bin/env python3
"""
Script to cleanup old files and their associated data.
This script helps manage storage by removing old files based on various criteria.
"""

import os
import sys
from datetime import datetime, timedelta
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

def get_db_session():
    """Create database session"""
    # Database URL from config
    DATABASE_URL = "mysql+pymysql://root:root@localhost/brahmavastu"
    
    engine = create_engine(DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    return SessionLocal()

def cleanup_old_files(days_old: int = 30, dry_run: bool = True):
    """
    Clean up files older than specified days.
    
    Args:
        days_old: Number of days after which files are considered old
        dry_run: If True, only show what would be deleted without actually deleting
    """
    db = get_db_session()
    try:
        cutoff_date = datetime.utcnow() - timedelta(days=days_old)
        
        # Find old files
        result = db.execute(text("""
            SELECT id, filename, path, created_at, size 
            FROM files 
            WHERE created_at < :cutoff_date
        """), {"cutoff_date": cutoff_date})
        
        old_files = result.fetchall()
        
        print(f"Found {len(old_files)} files older than {days_old} days")
        
        if dry_run:
            print("DRY RUN - No files will be deleted")
            for file in old_files:
                print(f"Would delete: {file.filename} (created: {file.created_at}, size: {file.size} bytes)")
        else:
            deleted_count = 0
            for file in old_files:
                try:
                    # Delete physical file
                    if os.path.exists(file.path):
                        os.remove(file.path)
                        print(f"Deleted physical file: {file.path}")
                    
                    # Delete database record (cascade will handle related records)
                    db.execute(text("DELETE FROM files WHERE id = :file_id"), {"file_id": file.id})
                    deleted_count += 1
                    print(f"Deleted database record: {file.filename}")
                    
                except Exception as e:
                    print(f"Error deleting {file.filename}: {e}")
            
            db.commit()
            print(f"Successfully deleted {deleted_count} files")
            
    except Exception as e:
        print(f"Error during cleanup: {e}")
        db.rollback()
    finally:
        db.close()

def cleanup_orphaned_floorplan_data(dry_run: bool = True):
    """
    Clean up floorplan analysis data that doesn't have associated files.
    
    Args:
        dry_run: If True, only show what would be deleted without actually deleting
    """
    db = get_db_session()
    try:
        # Find floorplan analyses with non-existent files
        result = db.execute(text("""
            SELECT fa.id, fa.file_id 
            FROM floorplan_analyses fa
            LEFT JOIN files f ON fa.file_id = f.id
            WHERE f.id IS NULL
        """))
        
        orphaned_analyses = result.fetchall()
        
        print(f"Found {len(orphaned_analyses)} orphaned floorplan analyses")
        
        if dry_run:
            print("DRY RUN - No data will be deleted")
            for analysis in orphaned_analyses:
                print(f"Would delete orphaned analysis ID: {analysis.id} (file_id: {analysis.file_id})")
        else:
            deleted_count = 0
            for analysis in orphaned_analyses:
                try:
                    db.execute(text("DELETE FROM floorplan_analyses WHERE id = :analysis_id"), 
                              {"analysis_id": analysis.id})
                    deleted_count += 1
                    print(f"Deleted orphaned analysis ID: {analysis.id}")
                except Exception as e:
                    print(f"Error deleting analysis {analysis.id}: {e}")
            
            db.commit()
            print(f"Successfully deleted {deleted_count} orphaned analyses")
            
    except Exception as e:
        print(f"Error during cleanup: {e}")
        db.rollback()
    finally:
        db.close()

def get_storage_stats():
    """Get storage statistics"""
    db = get_db_session()
    try:
        # Get total files and size
        result = db.execute(text("""
            SELECT COUNT(*) as total_files, SUM(size) as total_size
            FROM files
        """))
        stats = result.fetchone()
        
        # Get size by file type
        result = db.execute(text("""
            SELECT content_type, COUNT(*) as count, SUM(size) as size
            FROM files
            GROUP BY content_type
        """))
        file_types = result.fetchall()
        
        print(f"Storage Statistics:")
        print(f"Total files: {stats.total_files}")
        print(f"Total size: {stats.total_size / (1024*1024):.2f} MB" if stats.total_size else "Total size: 0 MB")
        print("\nBy file type:")
        for content_type, count, size in file_types:
            size_mb = (size or 0) / (1024*1024)
            print(f"  {content_type}: {count} files, {size_mb:.2f} MB")
            
    except Exception as e:
        print(f"Error getting stats: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="File cleanup utility")
    parser.add_argument("--action", choices=["cleanup-old", "cleanup-orphaned", "stats"], 
                       default="stats", help="Action to perform")
    parser.add_argument("--days", type=int, default=30, 
                       help="Number of days for old file cleanup")
    parser.add_argument("--execute", action="store_true", 
                       help="Actually perform the deletion (default is dry run)")
    
    args = parser.parse_args()
    
    if args.action == "cleanup-old":
        cleanup_old_files(days_old=args.days, dry_run=not args.execute)
    elif args.action == "cleanup-orphaned":
        cleanup_orphaned_floorplan_data(dry_run=not args.execute)
    elif args.action == "stats":
        get_storage_stats()
