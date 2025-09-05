#!/usr/bin/env python3
"""
Script to check and fix the videos table structure
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.db.session import SessionLocal
from sqlalchemy import text, inspect
from app.models.blog import Video

def check_videos_table():
    """Check if the videos table has the url column"""
    db = SessionLocal()
    try:
        # Check if url column exists
        inspector = inspect(db.bind)
        columns = inspector.get_columns('videos')
        column_names = [col['name'] for col in columns]
        
        print("Current columns in videos table:")
        for col in column_names:
            print(f"  - {col}")
        
        if 'url' in column_names:
            print("✅ URL column exists")
            return True
        else:
            print("❌ URL column missing")
            return False
            
    except Exception as e:
        print(f"Error checking table: {e}")
        return False
    finally:
        db.close()

def add_url_column():
    """Add the url column to videos table"""
    db = SessionLocal()
    try:
        # Add the url column
        db.execute(text("ALTER TABLE videos ADD COLUMN url VARCHAR(500) NULL"))
        db.commit()
        print("✅ URL column added successfully")
        return True
    except Exception as e:
        print(f"Error adding column: {e}")
        db.rollback()
        return False
    finally:
        db.close()

def update_existing_videos():
    """Update existing videos with proper URLs"""
    db = SessionLocal()
    try:
        # Get all videos without URLs
        result = db.execute(text("SELECT id, title FROM videos WHERE url IS NULL"))
        videos = result.fetchall()
        
        print(f"Found {len(videos)} videos without URLs")
        
        for video in videos:
            video_id, title = video
            # Generate a URL based on the video ID (this is a temporary fix)
            # In a real scenario, you'd need to check the MediaAsset table for the actual filename
            url = f"/static/media/videos/video_{video_id}.mp4"
            
            db.execute(text("UPDATE videos SET url = :url WHERE id = :id"), 
                      {"url": url, "id": video_id})
            print(f"Updated video {video_id}: {title}")
        
        db.commit()
        print("✅ Updated existing videos with URLs")
        return True
        
    except Exception as e:
        print(f"Error updating videos: {e}")
        db.rollback()
        return False
    finally:
        db.close()

def main():
    print("Checking videos table structure...")
    print("=" * 50)
    
    # Check if url column exists
    has_url_column = check_videos_table()
    
    if not has_url_column:
        print("\nAdding URL column...")
        if add_url_column():
            print("✅ URL column added")
        else:
            print("❌ Failed to add URL column")
            return
    
    # Update existing videos
    print("\nUpdating existing videos...")
    update_existing_videos()
    
    print("\n" + "=" * 50)
    print("Videos table check completed!")

if __name__ == "__main__":
    main()
