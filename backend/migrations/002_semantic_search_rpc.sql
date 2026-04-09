-- ==========================================
-- SEMANTIC SEARCH RPC FUNCTION
-- ==========================================
-- Add this to enable vector similarity search in Supabase
-- Execute in SQL Editor after running 001_init_schema.sql

-- Create RPC function for semantic food search using vector similarity
CREATE OR REPLACE FUNCTION search_foods(
  query_embedding VECTOR(384),
  similarity_threshold FLOAT DEFAULT 0.5,
  max_results INT DEFAULT 10
)
RETURNS TABLE (
  id UUID,
  name VARCHAR,
  calories FLOAT,
  protein FLOAT,
  fat FLOAT,
  carbs FLOAT,
  base_serving_size VARCHAR,
  is_user_contributed BOOLEAN,
  created_by UUID,
  created_at TIMESTAMP,
  similarity FLOAT
) AS $$
BEGIN
  RETURN QUERY
  SELECT
    f.id,
    f.name,
    f.calories,
    f.protein,
    f.fat,
    f.carbs,
    f.base_serving_size,
    f.is_user_contributed,
    f.created_by,
    f.created_at,
    1 - (f.embedding <=> query_embedding) as similarity
  FROM nutriguard.food_items f
  WHERE 1 - (f.embedding <=> query_embedding) > similarity_threshold
  ORDER BY f.embedding <=> query_embedding
  LIMIT max_results;
END;
$$ LANGUAGE plpgsql;

-- Create an index for faster vector searches (optional but recommended)
-- Requires pgvector extension (should already be enabled in Supabase)
CREATE INDEX IF NOT EXISTS idx_food_items_embedding ON nutriguard.food_items 
USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 100);
