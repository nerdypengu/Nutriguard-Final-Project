-- ==========================================
-- MEAL PROCESSING JOBS TABLE MIGRATION
-- ==========================================
-- Job tracking table for chat-based nutrition food processing with n8n integration

-- Create custom enum for job status (if not exists)
DO $$ BEGIN
  CREATE TYPE job_status AS ENUM ('PENDING', 'PROCESSING', 'COMPLETED', 'FAILED', 'CANCELLED');
EXCEPTION WHEN duplicate_object THEN null;
END $$;

-- Create meal_processing_jobs table (if not exists)
CREATE TABLE IF NOT EXISTS nutriguard.meal_processing_jobs (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL,
  status job_status DEFAULT 'PENDING',
  progress_message TEXT DEFAULT 'Memulai proses...',
  result JSONB DEFAULT NULL,
  created_at TIMESTAMPTZ DEFAULT now(),
  updated_at TIMESTAMPTZ DEFAULT now()
);

-- Create indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_meal_jobs_user_id ON nutriguard.meal_processing_jobs(user_id);
CREATE INDEX IF NOT EXISTS idx_meal_jobs_status ON nutriguard.meal_processing_jobs(status);
CREATE INDEX IF NOT EXISTS idx_meal_jobs_created_at ON nutriguard.meal_processing_jobs(created_at DESC);

-- DISABLE RLS - Backend uses service account which bypasses RLS anyway
-- No need for RLS on internal backend processing table
ALTER TABLE nutriguard.meal_processing_jobs DISABLE ROW LEVEL SECURITY;
