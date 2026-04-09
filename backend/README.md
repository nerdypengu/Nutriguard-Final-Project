# NutriGuard Backend API

A comprehensive nutrition tracking and meal planning backend powered by FastAPI and Supabase.

## Project Structure

```
backend/
├── core/
│   ├── __init__.py
│   └── supabase.py              # Supabase client initialization
├── services/
│   ├── __init__.py
│   ├── auth.py                  # Authentication logic
│   ├── users.py                 # User profiles & preferences
│   ├── food.py                  # Food items CRUD
│   ├── consumption_logs.py       # Consumption tracking
│   └── meal_plans.py            # Meal planning
├── router/
│   ├── __init__.py
│   ├── auth.py                  # Auth routes
│   ├── users.py                 # User routes
│   ├── food.py                  # Food routes
│   ├── consumption_logs.py       # Log routes
│   └── meal_plans.py            # Meal plan routes
├── migrations/
│   └── 001_init_schema.sql      # Database schema & RLS policies
├── main.py                      # FastAPI application entry point
├── requirements.txt             # Python dependencies
├── .env.example                 # Example environment variables
└── README.md
```

## Database Schema

The NutriGuard database consists of 5 main tables:

### 1. **users**
Central user table synced with Supabase Auth
- `id`: UUID (primary key, matches auth.users.id)
- `email`: User's email (unique)
- `discord_id`: Optional Discord account link
- `discord_username`: Discord username
- `is_subscribed`: Subscription status

### 2. **user_preferences**
User's nutrition targets and preferences
- `user_id`: Reference to users
- `diet_type`: Type of diet (Standard, Keto, Vegan, etc.)
- `target_calories`, `target_protein_g`, `target_carbs_g`, `target_fat_g`
- `preferred_generation_day`: Day for weekly meal plan generation

### 3. **food_items**
Master food database with nutritional info
- `name`: Food name
- `calories`, `protein`, `fat`, `carbs`: Nutritional values
- `base_serving_size`: Default serving (e.g., "100g")
- `unit_mappings`: JSON mappings for different units
- `tags`: Array of tags for filtering
- `is_user_contributed`: Whether user or admin-added
- `embedding`: Vector embedding for semantic search

### 4. **consumption_logs**
Daily food intake tracking (decoupled from food_items)
- `user_id`: Reference to users
- `food_name`: Name of consumed food
- `total_calories`, `total_protein`, `total_carbs`, `total_fat`: Cooked values
- `logged_at`: When the food was consumed
- `created_at`: When the log was created

### 5. **meal_plans**
Weekly/daily meal planning
- `user_id`: Reference to users
- `meal_name`: Name of the meal
- `total_calories`, `total_protein`, `total_carbs`, `total_fat`: Planned macros
- `planned_for_date`: Target date for the meal
- `status`: Planned, In Progress, Completed

## Setup Instructions

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Supabase

1. Create a project on [Supabase](https://supabase.com)
2. Get your project URL and anon key from the API settings
3. Copy `.env.example` to `.env` and fill in your credentials:

```bash
cp .env.example .env
```

```
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-anon-key
```

### 3. Create Database Tables

1. Go to SQL Editor in your Supabase dashboard
2. Copy the entire content of `migrations/001_init_schema.sql`
3. Paste and execute in the SQL Editor
4. This will create all tables, indexes, and RLS policies

**Or manually:**
- Use the Supabase UI to create each table following the schema mentioned above
- Make sure to set up foreign key relationships and enable RLS

### 4. Run the Server

```bash
python main.py
```

Or with Uvicorn directly:

```bash
uvicorn main:app --reload
```

The API will be available at `http://localhost:8000`

## API Documentation

Interactive documentation available at `http://localhost:8000/docs`

## API Endpoints

### Authentication (`/api/auth`)
- `POST /api/auth/signup` - Create new account
- `POST /api/auth/signin` - Login user
- `POST /api/auth/signout` - Logout user

### Users (`/api/users`)
- `POST /api/users/` - Create user profile
- `GET /api/users/` - Get all users
- `GET /api/users/{user_id}` - Get user by ID
- `GET /api/users/email/{email}` - Get user by email
- `PUT /api/users/{user_id}` - Update user
- `DELETE /api/users/{user_id}` - Delete user
- `POST /api/users/{user_id}/preferences` - Create preferences
- `GET /api/users/{user_id}/preferences` - Get preferences
- `PUT /api/users/{user_id}/preferences` - Update preferences
- `DELETE /api/users/{user_id}/preferences` - Delete preferences

### Food Items (`/api/food`)
- `GET /api/food/` - Get all food items
- `POST /api/food/` - Create food item (embeddings auto-generated)
- `GET /api/food/{food_id}` - Get food by ID
- `GET /api/food/search/by-name?name=...` - Search by name (text match)
- `GET /api/food/search/semantic?query=...` - **Semantic search using AI** 🧠
- `GET /api/food/search/by-tag?tag=...` - Filter by tag
- `PUT /api/food/{food_id}` - Update food item (embeddings updated automatically)
- `DELETE /api/food/{food_id}` - Delete food item

### Consumption Logs (`/api/logs`)
- `POST /api/logs/` - Log food consumption
- `GET /api/logs/user/{user_id}` - Get all logs for user
- `GET /api/logs/user/{user_id}/date/{target_date}` - Get logs for specific date
- `GET /api/logs/user/{user_id}/totals/{target_date}` - Get daily nutrition totals
- `PUT /api/logs/{log_id}` - Update log
- `DELETE /api/logs/{log_id}` - Delete log

### Meal Plans (`/api/meal-plans`)
- `POST /api/meal-plans/` - Create meal plan
- `GET /api/meal-plans/{plan_id}` - Get meal plan by ID
- `GET /api/meal-plans/user/{user_id}` - Get all plans for user
- `GET /api/meal-plans/user/{user_id}/date/{target_date}` - Get plans for specific date
- `PUT /api/meal-plans/{plan_id}` - Update meal plan
- `PATCH /api/meal-plans/{plan_id}/status` - Update status
- `DELETE /api/meal-plans/{plan_id}` - Delete meal plan

## Architecture

- **Core**: Database initialization and Supabase configuration
- **Services**: Business logic organized by domain (users, food, consumption, meals)
- **Router**: API endpoints calling service functions
- **Main.py**: FastAPI app setup with all routers registered

This clean separation ensures maintainability and scalability.

## Key Features ✨

- **JWT Authentication 🔐** - Secure token-based authentication for all protected endpoints
- **Discord OAuth Integration** - Sign in with Discord, ID automatically saved
- **Semantic Search 🧠** - AI-powered food search using embeddings (e.g., search "protein" to find chicken, beef, eggs, etc.)
- **Automatic Embeddings** - Food embeddings generated automatically on create/update
- **Vector Database** - Supabase pgvector integration for fast similarity searches
- **Daily Macro Tracking** - Calculate total nutrition intake per day
- **Meal Planning** - Plan and track meal status (Planned, In Progress, Completed)
- **User Preferences** - Customize diet goals and generation preferences
- **Flexible Food Database** - Support for both admin and user-contributed foods

**Documentation:**
- [AUTHENTICATION_GUIDE.md](AUTHENTICATION_GUIDE.md) - JWT & Discord OAuth setup & usage
- [SEMANTIC_SEARCH_GUIDE.md](SEMANTIC_SEARCH_GUIDE.md) - AI-powered search guide

## Security

- **JWT Bearer Tokens** - All protected endpoints require Authorization header with JWT token
- Row Level Security (RLS) policies enabled on all tables
- Users can only view/edit their own data
- Public food database accessible to all authenticated users
- Discord OAuth with secure token exchange

## Example Usage

### 1. Sign in and get JWT token:
```bash
curl -X POST "http://localhost:8000/api/auth/signin" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "password123"
  }'
```

**Response includes `access_token` from now on, use it in all protected requests:**
```bash
JWT="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

### 2. Use JWT token for all protected endpoints:
```bash
# Food endpoints - requires JWT
curl "http://localhost:8000/api/food/" \
  -H "Authorization: Bearer $JWT"

# Create food item
curl -X POST "http://localhost:8000/api/food/" \
  -H "Authorization: Bearer $JWT" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Chicken Breast",
    "calories": 165,
    "protein": 31,
    "fat": 3.6,
    "carbs": 0,
    "tags": ["protein", "lean"]
  }'

# Semantic search - requires JWT
curl "http://localhost:8000/api/food/search/semantic?query=protein" \
  -H "Authorization: Bearer $JWT"
```

### 3. Create meal plans with JWT:
```bash
curl -X POST "http://localhost:8000/api/meal-plans/" \
  -H "Authorization: Bearer $JWT" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "{user_id}",
    "meal_name": "Monday Breakfast",
    "total_calories": 450,
    "total_protein": 30,
    "total_carbs": 50,
    "total_fat": 15,
    "planned_for_date": "2024-04-01"
  }'
```

### 4. Log consumption and get daily totals:
```bash
# Log food
curl -X POST "http://localhost:8000/api/logs/" \
  -H "Authorization: Bearer $JWT" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "{user_id}",
    "food_name": "Chicken Breast",
    "total_calories": 165,
    "total_protein": 31,
    "total_carbs": 0,
    "total_fat": 3.6
  }'

# Get daily totals
curl "http://localhost:8000/api/logs/user/{user_id}/totals/2024-04-01" \
  -H "Authorization: Bearer $JWT"
```

### 5. Discord OAuth (Optional):
```bash
# Get Discord login URL
curl "http://localhost:8000/api/auth/discord/login"

# Exchange Discord code for JWT token
curl -X POST "http://localhost:8000/api/auth/discord/callback?code=DISCORD_CODE"

# Response includes JWT token - use like email/password authentication
```
