-- Migration: 001_create_initial_tables
-- Description: Create initial database tables
-- Created: 2024-12-13
-- Type: DDL

-- This migration creates all the base tables for the student management system.
-- It will be executed when running `flask db upgrade` for the first time.

-- Run the complete init.sql to create all tables and initial data
-- This migration references the init.sql to avoid code duplication
SOURCE ../../init.sql;