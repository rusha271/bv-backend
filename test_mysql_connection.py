#!/usr/bin/env python3
"""
MySQL connection test script.
This script helps you find the correct MySQL credentials.
"""

import pymysql
import getpass

def test_mysql_connections():
    """Test different MySQL connection configurations"""
    
    print("🔍 Testing MySQL connections...")
    print("=" * 50)
    
    # Test configurations to try
    configs = [
        {"user": "root", "password": "", "desc": "Root without password"},
        {"user": "root", "password": "root", "desc": "Root with password 'root'"},
        {"user": "root", "password": "admin", "desc": "Root with password 'admin'"},
        {"user": "root", "password": "password", "desc": "Root with password 'password'"},
        {"user": "user", "password": "root", "desc": "User 'user' with password 'root'"},
        {"user": "brahmavastu", "password": "password", "desc": "User 'brahmavastu' with password 'password'"},
    ]
    
    working_configs = []
    
    for config in configs:
        try:
            print(f"Testing: {config['desc']}")
            connection = pymysql.connect(
                host="localhost",
                user=config["user"],
                password=config["password"],
                charset='utf8mb4'
            )
            print(f"✅ SUCCESS: {config['desc']}")
            working_configs.append(config)
            connection.close()
            
        except pymysql.err.OperationalError as e:
            print(f"❌ FAILED: {config['desc']} - {e}")
        except Exception as e:
            print(f"❌ ERROR: {config['desc']} - {e}")
    
    print("\n" + "=" * 50)
    
    if working_configs:
        print("✅ Working configurations found:")
        for config in working_configs:
            print(f"   - {config['desc']}")
            print(f"     DATABASE_URL=mysql+pymysql://{config['user']}:{config['password']}@localhost/brahmavastu")
        print("\n💡 Update your .env file with one of these working configurations!")
    else:
        print("❌ No working configurations found.")
        print("\n🔧 Manual setup required:")
        print("1. Make sure MySQL server is running")
        print("2. Try connecting manually:")
        print("   mysql -u root -p")
        print("3. Create a new user if needed:")
        print("   CREATE USER 'brahmavastu'@'localhost' IDENTIFIED BY 'password';")
        print("   GRANT ALL PRIVILEGES ON *.* TO 'brahmavastu'@'localhost';")
        print("   FLUSH PRIVILEGES;")

def manual_connection_test():
    """Allow manual input of credentials"""
    print("\n🔧 Manual connection test:")
    user = input("Enter MySQL username (default: root): ").strip() or "root"
    password = getpass.getpass("Enter MySQL password (if any): ").strip()
    
    try:
        connection = pymysql.connect(
            host="localhost",
            user=user,
            password=password,
            charset='utf8mb4'
        )
        print(f"✅ SUCCESS: Connected with user '{user}'")
        print(f"📝 Use this in your .env file:")
        print(f"   DATABASE_URL=mysql+pymysql://{user}:{password}@localhost/brahmavastu")
        connection.close()
        
    except Exception as e:
        print(f"❌ FAILED: {e}")

if __name__ == "__main__":
    test_mysql_connections()
    print("\n" + "=" * 50)
    manual_connection_test() 