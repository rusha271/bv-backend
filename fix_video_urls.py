#!/usr/bin/env python3
"""
Script to fix video URLs in the database
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.db.session import SessionLocal
from sqlalchemy import text
from app.models.blog import Video, MediaAsset

def add_url_column_if_missing():
    """Add url column to videos table if it doesn't exist"""
    db = SessionLocal()
    try:
        # Check if column exists
        result = db.execute(text("SHOW COLUMNS FROM videos LIKE 'url'"))
        if not result.fetchone():
            print("Adding url column to videos table...")
            db.execute(text("ALTER TABLE videos ADD COLUMN url VARCHAR(500) NULL"))
            db.commit()
            print("✅ URL column added")
        else:
            print("✅ URL column already exists")
        return True
    except Exception as e:
        print(f"Error adding column: {e}")
        db.rollback()
        return False
    finally:
        db.close()

def update_video_urls():
    """Update video URLs from MediaAsset table"""
    db = SessionLocal()
    try:
        # Get all videos
        videos = db.query(Video).all()
        print(f"Found {len(videos)} videos to update")
        
        updated_count = 0
        for video in videos:
            # Find the corresponding MediaAsset
            media_asset = db.query(MediaAsset).filter(
                MediaAsset.content_id == video.id,
                MediaAsset.asset_type == "video"
            ).first()
            
            if media_asset and media_asset.filename:
                # Update the video URL
                video.url = f"/static/media/videos/{media_asset.filename}"
                updated_count += 1
                print(f"Updated video {video.id}: {video.title} -> {video.url}")
            else:
                print(f"No MediaAsset found for video {video.id}: {video.title}")
        
        db.commit()
        print(f"✅ Updated {updated_count} videos")
        return True
        
    except Exception as e:
        print(f"Error updating videos: {e}")
        db.rollback()
        return False
    finally:
        db.close()

def main():
    print("Fixing video URLs...")
    print("=" * 50)
    
    # Add URL column if missing
    if not add_url_column_if_missing():
        print("❌ Failed to add URL column")
        return
    
    # Update video URLs
    if not update_video_urls():
        print("❌ Failed to update video URLs")
        return
    
    print("\n" + "=" * 50)
    print("✅ Video URL fix completed successfully!")

if __name__ == "__main__":
    main()
