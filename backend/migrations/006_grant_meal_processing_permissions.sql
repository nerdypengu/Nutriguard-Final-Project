-- ==========================================
-- GRANT PERMISSIONS FOR MEAL PROCESSING JOBS
-- ==========================================
-- This migration grants necessary permissions for the meal_processing_jobs table
-- to the service role so backend can insert/update/delete records

-- Grant usage on the schema to service role
GRANT USAGE ON SCHEMA nutriguard TO service_role;

-- Grant all permissions on meal_processing_jobs table to service role
GRANT SELECT, INSERT, UPDATE, DELETE ON nutriguard.meal_processing_jobs TO service_role;

-- Also ensure authenticated users can access the table
GRANT SELECT, INSERT, UPDATE, DELETE ON nutriguard.meal_processing_jobs TO authenticated;

-- Grant usage on job_status enum
GRANT USAGE ON TYPE nutriguard.job_status TO service_role;
GRANT USAGE ON TYPE nutriguard.job_status TO authenticated;
