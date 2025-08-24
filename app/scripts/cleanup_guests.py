#!/usr/bin/env python3
"""
Script to clean up expired guest accounts.
This should be run as a scheduled task (e.g., daily via cron).
"""

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from app.db.session import SessionLocal
from app.services.guest_service import guest_service
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def cleanup_expired_guests(days_old: int = 7):
    """Clean up guest accounts older than specified days"""
    db = SessionLocal()
    try:
        deleted_count = guest_service.cleanup_expired_guests(db, days_old)
        logger.info(f"Cleaned up {deleted_count} expired guest accounts (older than {days_old} days)")
        return deleted_count
    except Exception as e:
        logger.error(f"Error cleaning up guest accounts: {str(e)}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Clean up expired guest accounts")
    parser.add_argument(
        "--days", 
        type=int, 
        default=7, 
        help="Delete guest accounts older than this many days (default: 7)"
    )
    
    args = parser.parse_args()
    
    try:
        deleted_count = cleanup_expired_guests(args.days)
        print(f"Successfully cleaned up {deleted_count} expired guest accounts")
    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(1)
