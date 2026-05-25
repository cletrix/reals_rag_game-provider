-- Migration: Add password_hash to existing users table
-- Version: 004
-- Date: 2026-05-25
-- Note: Adds authentication to the existing users table from schema-auditoria-enterprise.sql

-- Add password_hash column
ALTER TABLE users ADD COLUMN IF NOT EXISTS password_hash VARCHAR(255);

-- Update existing users with default passwords
-- Password hash for 'admin123' using bcrypt
UPDATE users 
SET password_hash = '$2b$12$I3Nq0VMRGtwaFmEfXbYqOexlaguVHj06pzsVng0S/jYw1Fif3raru'
WHERE email = 'admin@empresa.com';

-- Password hash for 'dev123' using bcrypt
UPDATE users 
SET password_hash = '$2b$12$OWX8gkFw/VeDaSze4zB5UudCo7NmcrQFHPU7bkfCcdlRe4m/xumd2'
WHERE email IN ('dev1@empresa.com', 'dev2@empresa.com', 'bets1@empresa.com', 'rh1@empresa.com');

-- Add index on password_hash for faster lookups
CREATE INDEX IF NOT EXISTS idx_users_password_hash ON users(password_hash);

-- Add comment
COMMENT ON COLUMN users.password_hash IS 'Bcrypt hash of the password for authentication';
