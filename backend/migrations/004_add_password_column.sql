-- ==========================================
-- ADD PASSWORD COLUMN TO USERS TABLE
-- ==========================================
-- This migration adds a password column for storing hashed passwords

ALTER TABLE nutriguard.users 
ADD COLUMN password_hash VARCHAR(255) NOT NULL DEFAULT '';

-- Update the default to empty string for existing records
UPDATE nutriguard.users SET password_hash = '' WHERE password_hash IS NULL;

-- Add a column to track last login
ALTER TABLE nutriguard.users 
ADD COLUMN last_login TIMESTAMP DEFAULT NULL;
