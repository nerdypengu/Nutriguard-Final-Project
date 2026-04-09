from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from router.auth import router as auth_router
from router.food import router as food_router
from router.users import router as users_router
from router.consumption_logs import router as consumption_logs_router
from router.meal_plans import router as meal_plans_router
from router.bot import router as bot_router
from router.bot_food import router as bot_food_router
from router.bot_meal_plans import router as bot_meal_plans_router
from router.bot_logs import router as bot_logs_router
from router.bot_users import router as bot_users_router
from router.meal_processing import router as meal_processing_router
from core.rate_limit import limiter
from core.redis import close_redis

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

# Include routers
app.include_router(auth_router)
app.include_router(users_router)
app.include_router(food_router)
app.include_router(consumption_logs_router)
app.include_router(meal_plans_router)
app.include_router(bot_router)
app.include_router(bot_food_router)
app.include_router(bot_meal_plans_router)
app.include_router(bot_logs_router)
app.include_router(bot_users_router)
app.include_router(meal_processing_router)

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
    return {"status": "ok"}


@app.on_event("shutdown")
async def shutdown_event():
    """Close Redis connection on shutdown"""
    await close_redis()