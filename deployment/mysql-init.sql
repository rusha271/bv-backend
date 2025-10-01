-- MySQL Initialization Script for Brahma Vastu Backend
-- This script runs when the MySQL container starts for the first time

-- Create database if it doesn't exist (already created by MYSQL_DATABASE env var)
-- CREATE DATABASE IF NOT EXISTS brahmavastu;

-- Use the database
USE brahmavastu;

-- Create user if it doesn't exist (already created by MYSQL_USER env var)
-- CREATE USER IF NOT EXISTS 'bvuser'@'%' IDENTIFIED BY 'bv_password';

-- Grant all privileges to the user
GRANT ALL PRIVILEGES ON brahmavastu.* TO 'bvuser'@'%';

-- Grant privileges for root user (for development)
GRANT ALL PRIVILEGES ON brahmavastu.* TO 'root'@'%';

-- Flush privileges to ensure they take effect
FLUSH PRIVILEGES;

-- Set MySQL configuration for development
SET GLOBAL sql_mode = 'STRICT_TRANS_TABLES,NO_ZERO_DATE,NO_ZERO_IN_DATE,ERROR_FOR_DIVISION_BY_ZERO';
SET GLOBAL innodb_buffer_pool_size = 128M;
SET GLOBAL max_connections = 200;

-- Create a simple test table to verify connection
CREATE TABLE IF NOT EXISTS connection_test (
    id INT AUTO_INCREMENT PRIMARY KEY,
    message VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insert a test record
INSERT INTO connection_test (message) VALUES ('Database connection successful');

-- Show database information
SELECT 'Brahma Vastu Database Initialized Successfully' as status;
SELECT DATABASE() as current_database;
SELECT USER() as current_user;
