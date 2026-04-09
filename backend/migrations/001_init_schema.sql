-- ==========================================
-- NUTRIGUARD DATABASE SCHEMA MIGRATION
-- ==========================================
-- Execute these SQL commands in your Supabase SQL Editor

-- Enable UUID extension (if not already enabled)
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- 1. Users Table
CREATE TABLE nutriguard.users (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  email VARCHAR(255) UNIQUE NOT NULL,
  discord_id VARCHAR(255) UNIQUE,
  discord_username VARCHAR(255),
  is_subscribed BOOLEAN DEFAULT false,
  created_at TIMESTAMP DEFAULT NOW()
);

-- 2. User Preferences Table
CREATE TABLE nutriguard.user_preferences (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID UNIQUE NOT NULL,
  diet_type VARCHAR(50) DEFAULT 'Standard',
  target_calories INTEGER NOT NULL,
  target_protein_g INTEGER NOT NULL,
  target_carbs_g INTEGER NOT NULL,
  target_fat_g INTEGER NOT NULL,
  preferred_generation_day VARCHAR(20) DEFAULT 'Sunday',
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW(),
  FOREIGN KEY (user_id) REFERENCES nutriguard.users(id) ON DELETE CASCADE
);

-- 3. Food Items Table
CREATE TABLE nutriguard.food_items (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name VARCHAR(255) NOT NULL,
  calories FLOAT NOT NULL,
  protein FLOAT NOT NULL,
  fat FLOAT NOT NULL,
  carbs FLOAT NOT NULL,
  base_serving_size VARCHAR(50) DEFAULT '100g',
  is_user_contributed BOOLEAN DEFAULT false,
  created_by UUID,
  embedding VECTOR(384),
  created_at TIMESTAMP DEFAULT NOW(),
  FOREIGN KEY (created_by) REFERENCES nutriguard.users(id) ON DELETE SET NULL
);

-- 4. Consumption Logs Table
CREATE TABLE nutriguard.consumption_logs (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL,
  food_name VARCHAR(255) NOT NULL,
  total_calories FLOAT NOT NULL,
  total_protein FLOAT NOT NULL,
  total_carbs FLOAT NOT NULL,
  total_fat FLOAT NOT NULL,
  logged_at TIMESTAMP DEFAULT NOW(),
  created_at TIMESTAMP DEFAULT NOW(),
  FOREIGN KEY (user_id) REFERENCES nutriguard.users(id) ON DELETE CASCADE
);

-- 5. Meal Plans Table
CREATE TABLE nutriguard.meal_plans (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL,
  meal_name VARCHAR(255) NOT NULL,
  total_calories FLOAT NOT NULL,
  total_protein FLOAT NOT NULL,
  total_carbs FLOAT NOT NULL,
  total_fat FLOAT NOT NULL,
  planned_for_date DATE NOT NULL,
  status VARCHAR(50) DEFAULT 'Planned',
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW(),
  FOREIGN KEY (user_id) REFERENCES nutriguard.users(id) ON DELETE CASCADE
);

-- ==========================================
-- INDEXES (for performance)
-- ==========================================

CREATE INDEX idx_users_email ON nutriguard.users(email);
CREATE INDEX idx_users_discord_id ON nutriguard.users(discord_id);
CREATE INDEX idx_user_preferences_user_id ON nutriguard.user_preferences(user_id);
CREATE INDEX idx_food_items_name ON nutriguard.food_items(name);
CREATE INDEX idx_food_items_created_by ON nutriguard.food_items(created_by);
CREATE INDEX idx_consumption_logs_user_id ON nutriguard.consumption_logs(user_id);
CREATE INDEX idx_consumption_logs_logged_at ON nutriguard.consumption_logs(logged_at);
CREATE INDEX idx_meal_plans_user_id ON nutriguard.meal_plans(user_id);
CREATE INDEX idx_meal_plans_planned_for_date ON nutriguard.meal_plans(planned_for_date);

-- ==========================================
-- ENABLE ROW LEVEL SECURITY (RLS)
-- ==========================================

ALTER TABLE nutriguard.users ENABLE ROW LEVEL SECURITY;
ALTER TABLE nutriguard.user_preferences ENABLE ROW LEVEL SECURITY;
ALTER TABLE nutriguard.food_items ENABLE ROW LEVEL SECURITY;
ALTER TABLE nutriguard.consumption_logs ENABLE ROW LEVEL SECURITY;
ALTER TABLE nutriguard.meal_plans ENABLE ROW LEVEL SECURITY;

-- RLS Policy: Users can view their own profile
CREATE POLICY "Users can view own profile"
ON nutriguard.users FOR SELECT
TO authenticated
USING (auth.uid() = id);

-- RLS Policy: Users can view their own preferences
CREATE POLICY "Users can view own preferences"
ON nutriguard.user_preferences FOR SELECT
TO authenticated
USING (auth.uid() = user_id);

-- RLS Policy: Users can view their own consumption logs
CREATE POLICY "Users can view own logs"
ON nutriguard.consumption_logs FOR SELECT
TO authenticated
USING (auth.uid() = user_id);

-- RLS Policy: Users can view their own meal plans
CREATE POLICY "Users can view own meal plans"
ON nutriguard.meal_plans FOR SELECT
TO authenticated
USING (auth.uid() = user_id);

-- RLS Policy: Users can view all public food items
CREATE POLICY "Users can view public food items"
ON nutriguard.food_items FOR SELECT
TO authenticated
USING (is_user_contributed = false OR created_by = auth.uid());
