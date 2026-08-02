-- DDL Initialization script setting up Snowflake databases, stages, vector search indexes, and RBAC tables.
-- Execution requires ACCOUNTADMIN or SYSADMIN roles in Snowflake.

CREATE DATABASE IF NOT EXISTS WORKMATE_DB;
USE DATABASE WORKMATE_DB;
CREATE SCHEMA IF NOT EXISTS PUBLIC;
USE SCHEMA PUBLIC;

-- Raw Document Storage Stage
CREATE STAGE IF NOT EXISTS KNOWLEDGE_STAGE
    FILE_FORMAT = (TYPE = 'AUTO');
