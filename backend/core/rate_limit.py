"""
Rate limiting utilities for NutriGuard Backend using Redis and slowapi.
Used to prevent API abuse and ensure fair usage.
"""
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi import Request

# Initialize rate limiter with Redis backend
# Using get_remote_address to identify clients by IP
limiter = Limiter(key_func=get_remote_address)

# Pre-defined rate limit strategies
RATE_LIMITS = {
    "auth": "5/minute",           # 5 requests per minute for auth endpoints
    "search": "30/minute",        # 30 requests per minute for search
    "food_write": "20/minute",    # 20 requests per minute for creating/updating food
    "general": "100/minute",      # 100 requests per minute for general endpoints
}
