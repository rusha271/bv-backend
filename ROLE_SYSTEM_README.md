# Role-Based Access Control System

## Overview
- Separate Role table with id and name fields
- Page-wise access control system
- Encryption/decryption instead of hashing
- Database name: "brahmavastu" (MySQL)

## Database Structure
- Role table: id, name
- PageAccess table: role_id, page_name, permissions
- User table: updated to use role_id foreign key

## Setup
1. Install: `pip install -r requirements.txt`
2. Set environment variables in .env:
   ```
   DATABASE_URL=mysql+pymysql://user:root@localhost/brahmavastu
   ENCRYPTION_KEY=your-32-byte-base64-encoded-key
   JWT_SECRET_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiYWRtaW4iOnRydWUsImlhdCI6MTUxNjIzOTAyMn0.KMUFsIDTnFmyG3nMiGM6H9FNFUROf3wh7SmqJp-QV30
   ```
3. Run: `python init_database.py`

## Default Roles
- admin: Full access
- user: Limited access
- consultant: Moderate access 