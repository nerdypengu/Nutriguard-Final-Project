-- ==========================================
-- GRANT PERMISSIONS ON NUTRIGUARD SCHEMA
-- ==========================================
-- This migration grants necessary permissions to authenticated users
-- so they can access tables in the custom nutriguard schema

-- Grant usage on the schema to authenticated users
GRANT USAGE ON SCHEMA nutriguard TO authenticated;
GRANT USAGE ON SCHEMA nutriguard TO anon;

-- Grant permissions on all tables in nutriguard schema
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA nutriguard TO authenticated;
GRANT SELECT ON ALL TABLES IN SCHEMA nutriguard TO anon;

-- Grant permissions on all sequences (for auto-increment IDs)
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA nutriguard TO authenticated;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA nutriguard TO anon;

-- Grant permissions on specific tables
GRANT SELECT, INSERT, UPDATE, DELETE ON nutriguard.users TO authenticated;
GRANT SELECT, INSERT, UPDATE, DELETE ON nutriguard.user_preferences TO authenticated;
GRANT SELECT, INSERT, UPDATE, DELETE ON nutriguard.food_items TO authenticated;
GRANT SELECT, INSERT, UPDATE, DELETE ON nutriguard.consumption_logs TO authenticated;
GRANT SELECT, INSERT, UPDATE, DELETE ON nutriguard.meal_plans TO authenticated;

-- Set default privileges for future tables
ALTER DEFAULT PRIVILEGES IN SCHEMA nutriguard GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO authenticated;
ALTER DEFAULT PRIVILEGES IN SCHEMA nutriguard GRANT USAGE, SELECT ON SEQUENCES TO authenticated;
