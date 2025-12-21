-- Database initialization script for Digestible
-- This script runs when the PostgreSQL container starts for the first time

-- Create the digestible database (if not exists)
-- Note: The database is already created via POSTGRES_DB environment variable

-- Set up any initial database configuration here
-- For example, you could add extensions or initial data

-- Enable necessary extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- You can add any initial data setup here if needed
-- For now, the database schema will be created by Alembic migrations