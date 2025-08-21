# MySQL Setup Guide for Brahmavastu

## Prerequisites
- MySQL Server installed and running
- Python 3.8+ installed

## Step 1: Install Dependencies
```bash
pip install -r requirements.txt
```

## Step 2: Create Environment File
Create a `.env` file in the root directory with the following content:

```env
# Database Configuration
DATABASE_URL=mysql+pymysql://user:root@localhost/brahmavastu

# Security
JWT_SECRET_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiYWRtaW4iOnRydWUsImlhdCI6MTUxNjIzOTAyMn0.KMUFsIDTnFmyG3nMiGM6H9FNFUROf3wh7SmqJp-QV30
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=60

# Encryption
ENCRYPTION_KEY=your-32-byte-base64-encoded-encryption-key

# Environment
ENV=development

# Frontend Origins (for CORS)
FRONTEND_ORIGINS=["http://localhost:3000", "http://localhost:3001"]
```

## Step 3: Set up MySQL Database
```bash
python setup_mysql.py
```

This script will:
- Create the `brahmavastu` database
- Set up proper character encoding (utf8mb4)
- Create database user if needed

## Step 4: Initialize Database with Roles
```bash
python init_database.py
```

This script will:
- Create all database tables
- Create default roles (admin, user, consultant)
- Set up page access permissions

## Step 5: Start the Application
```bash
uvicorn app.main:app --reload
```

## Database Connection Details

### Default Configuration
- **Host**: localhost
- **Database**: brahmavastu
- **User**: user (or root)
- **Password**: password (or empty for root)
- **Character Set**: utf8mb4

### Custom Configuration
To use different credentials, update the `DATABASE_URL` in your `.env` file:

```env
DATABASE_URL=mysql+pymysql://your_user:your_password@your_host/brahmavastu
```

## Troubleshooting

### Connection Issues
1. Ensure MySQL server is running
2. Check if the user has proper permissions
3. Verify the database name is correct

### Permission Issues
If you get permission errors, you may need to:
1. Use root user temporarily
2. Grant proper permissions to your MySQL user
3. Create the database manually

### Character Encoding
The database is created with `utf8mb4` character set to support all Unicode characters including emojis.

## Security Notes
- Change default passwords in production
- Use strong encryption keys
- Store sensitive data in environment variables
- Never commit `.env` files to version control 