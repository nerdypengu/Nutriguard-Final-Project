-- ==========================================
-- ADD MEAL_TYPE ENUM
-- ==========================================
-- Execute these SQL commands in your Supabase SQL Editor

-- Create the ENUM type (Optional but we can just use VARCHAR for simplicity based on previous implementation)
-- However, we'll use VARCHAR to be consistent with `status` which is VARCHAR(50).

ALTER TABLE nutriguard.meal_plans ADD COLUMN meal_type VARCHAR(50) DEFAULT 'ADDITIONAL';

-- If you prefer using ENUM strictly:
-- CREATE TYPE nutriguard.meal_type_enum AS ENUM ('BREAKFAST', 'LUNCH', 'DINNER', 'ADDITIONAL');
-- ALTER TABLE nutriguard.meal_plans ADD COLUMN meal_type nutriguard.meal_type_enum DEFAULT 'ADDITIONAL';
