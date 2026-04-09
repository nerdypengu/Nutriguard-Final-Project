from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from core.rate_limit import limiter
from core.redis import close_redis
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="NutriGuard Backend API",
    description="A comprehensive nutrition tracking and meal planning backend powered by Supabase",
    version="2.0.0"
)

# Set the limiter for rate limiting
app.state.limiter = limiter

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure rate limiting middleware
app.add_middleware(SlowAPIMiddleware)

# Include routers with error handling
routers_modules = [
    "router.auth",
    "router.food",
    "router.users",
    "router.consumption_logs",
    "router.meal_plans",
    "router.bot",
    "router.bot_food",
    "router.bot_meal_plans",
    "router.bot_logs",
    "router.bot_users",
    "router.meal_processing",
]

for module_path in routers_modules:
    try:
        module = __import__(module_path, fromlist=["router"])
        app.include_router(module.router)
        logger.info(f"✓ Loaded router: {module_path}")
    except Exception as e:
        logger.error(f"✗ Failed to load router {module_path}: {e}")
        import traceback
        traceback.print_exc()

@app.get("/")
async def root():
    return {
        "message": "Welcome to NutriGuard Backend API",
        "version": "2.0.0",
        "endpoints": {
            "auth": "/api/auth",
            "users": "/api/users",
            "food": "/api/food",
            "logs": "/api/logs",
            "meal_plans": "/api/meal-plans",
            "bot": "/api/bot",
            "docs": "/docs"
        }
    }

@app.get("/health")
async def health_check():
    return {"status": "ok", "message": "Server is running"}


@app.on_event("shutdown")
async def shutdown_event():
    """Close Redis connection on shutdown"""
    await close_redis()