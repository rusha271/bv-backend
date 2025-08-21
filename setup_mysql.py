#!/usr/bin/env python3
"""
MySQL database setup script for Brahmavastu application.
This script creates the MySQL database and user.
"""

import pymysql
from urllib.parse import urlparse
import os
from app.core.config import settings

def setup_mysql_database():
    """Create MySQL database and user for Brahmavastu application"""
    
    # Parse database URL to get connection details
    # Format: mysql+pymysql://user:root@localhost/brahmavastu
    db_url = settings.DATABASE_URL
    
    # Extract components from the URL
    parsed = urlparse(settings.DATABASE_URL)

    user = parsed.username or "root"
    password = parsed.password or ""
    host = parsed.hostname or "localhost"
    database = parsed.path.lstrip('/') or "brahmavastu"

    print(f"Attempting to connect with user: {user}")
    print(f"Host: {host}")
    print(f"Database: {database}")
    
    # Try to connect with provided credentials first
    try:
        connection = pymysql.connect(
            host=host,
            user=user,
            password=password,
            charset='utf8mb4'
        )
        print("✅ Successfully connected with provided credentials!")
        
    except pymysql.err.OperationalError as e:
        if "Access denied" in str(e):
            print("❌ Access denied with provided credentials.")
            print("Trying to connect with root user...")
            
            # Try with root user (common fallback)
            try:
                connection = pymysql.connect(
                    host=host,
                    user="root",
                    password="",  # Empty password for root
                    charset='utf8mb4'
                )
                print("✅ Successfully connected with root user!")
                user = "root"  # Update user for later use
                
            except pymysql.err.OperationalError as root_error:
                print("❌ Failed to connect with root user as well.")
                print("\n🔧 Troubleshooting steps:")
                print("1. Make sure MySQL server is running")
                print("2. Check if you can connect manually:")
                print("   mysql -u root -p")
                print("3. If root has a password, update your .env file:")
                print("   DATABASE_URL=mysql+pymysql://root:your_root_password@localhost/brahmavastu")
                print("4. Or create a new MySQL user:")
                print("   CREATE USER 'brahmavastu'@'localhost' IDENTIFIED BY 'password';")
                print("   GRANT ALL PRIVILEGES ON *.* TO 'brahmavastu'@'localhost';")
                print("   FLUSH PRIVILEGES;")
                raise Exception(f"MySQL connection failed: {e}. Root connection also failed: {root_error}")
        else:
            raise e
    
    cursor = connection.cursor()
    
    try:
        # Create database if it doesn't exist
        print(f"Creating database '{database}' if it doesn't exist...")
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS `{database}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
        
        # Create application user if not using root
        if user != "root":
            print(f"Creating user '{user}' if it doesn't exist...")
            try:
                cursor.execute(f"CREATE USER IF NOT EXISTS '{user}'@'localhost' IDENTIFIED BY '{password}'")
                cursor.execute(f"GRANT ALL PRIVILEGES ON `{database}`.* TO '{user}'@'localhost'")
                cursor.execute("FLUSH PRIVILEGES")
                print(f"✅ User '{user}' created/updated successfully!")
            except Exception as e:
                print(f"⚠️  Note: User creation failed (this is normal if user already exists): {e}")
        
        connection.commit()
        print(f"✅ MySQL database '{database}' setup completed successfully!")
        print(f"📝 Connection string: mysql+pymysql://{user}:*****@{host}/{database}")
        print(f"💡 Update your .env file with the working credentials!")
        
    except Exception as e:
        print(f"❌ Error during database setup: {e}")
        connection.rollback()
        raise
    finally:
        cursor.close()
        connection.close()

if __name__ == "__main__":
    print("Setting up MySQL database for Brahmavastu application...")
    setup_mysql_database()
    print("MySQL setup complete!")
