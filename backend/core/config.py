"""
Configuration and settings for NutriGuard Backend
"""
import os
from datetime import timedelta
from dotenv import load_dotenv

load_dotenv()

# JWT Configuration
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key-change-this-in-production")
JWT_ALGORITHM = "HS256"
JWT_EXPIRATION_HOURS = 24
ACCESS_TOKEN_EXPIRE_TIMEDELTA = timedelta(hours=JWT_EXPIRATION_HOURS)

# Supabase
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

# Redis Configuration
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
REDIS_CACHE_TTL = int(os.getenv("REDIS_CACHE_TTL", "3600"))  # Default 1 hour
REDIS_RATE_LIMIT_TTL = int(os.getenv("REDIS_RATE_LIMIT_TTL", "60"))  # Default 1 minute

# Bot Service Account Configuration
BOT_API_KEY = os.getenv("BOT_API_KEY", "your-bot-api-key-change-in-production")
BOT_SERVICE_ID = os.getenv("BOT_SERVICE_ID", "nutriguard-bot")

# n8n Webhook Configuration
N8N_WEBHOOK_URL = os.getenv("N8N_WEBHOOK_URL", "")

# Settings
DEBUG = os.getenv("DEBUG", "False").lower() == "true"

# Keycloak Configuration
KEYCLOAK_SERVER_URL = os.getenv("KEYCLOAK_SERVER_URL", "http://localhost:8080")
KEYCLOAK_REALM = os.getenv("KEYCLOAK_REALM", "nutriguard")
KEYCLOAK_CLIENT_ID = os.getenv("KEYCLOAK_CLIENT_ID", "nutriguard-backend")
KEYCLOAK_CLIENT_SECRET = os.getenv("KEYCLOAK_CLIENT_SECRET", "")
