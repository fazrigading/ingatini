"""PostgreSQL initialization script."""
-- Create database if it doesn't exist
CREATE DATABASE ingatini_db;

-- Connect to the database
\c ingatini_db;

-- Enable pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;
