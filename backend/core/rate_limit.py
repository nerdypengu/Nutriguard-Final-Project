"""
Rate limiting utilities for NutriGuard Backend using Redis and slowapi.
Used to prevent API abuse and ensure fair usage.
Includes fallback for production environments without Redis (e.g., Vercel).
"""
from slowapi import Limiter
from slowapi.util import get_remote_address
import logging
from datetime import datetime, timedelta
from collections import defaultdict

logger = logging.getLogger(__name__)

# Initialize rate limiter with memory-based fallback
# Using get_remote_address to identify clients by IP
limiter = Limiter(key_func=get_remote_address, default_limits=[])

# In-memory fallback rate limit tracking
# Structure: {key: [(timestamp, count), ...]}
_memory_limits = defaultdict(list)

# Pre-defined rate limit strategies
RATE_LIMITS = {
    "auth": "5/minute",           # 5 requests per minute for auth endpoints
    "search": "30/minute",        # 30 requests per minute for search
    "food_write": "20/minute",    # 20 requests per minute for creating/updating food
    "general": "100/minute",      # 100 requests per minute for general endpoints
}


async def check_memory_rate_limit(key: str, limit: str) -> bool:
    """
    Memory-based rate limit checker (fallback for Redis).
    
    Args:
        key (str): Rate limit key (usually client IP)
        limit (str): Rate limit string (e.g., "5/minute", "100/minute")
        
    Returns:
        bool: True if within limit, False if exceeded
    """
    try:
        # Parse limit string
        count, period = limit.split('/')
        count = int(count)
        
        # Calculate time window
        if period == "minute":
            time_window = timedelta(minutes=1)
        elif period == "hour":
            time_window = timedelta(hours=1)
        elif period == "second":
            time_window = timedelta(seconds=1)
        else:
            return True  # Invalid format, allow through
        
        now = datetime.now()
        cutoff_time = now - time_window
        
        # Remove old entries outside the window
        _memory_limits[key] = [
            timestamp for timestamp in _memory_limits[key]
            if timestamp > cutoff_time
        ]
        
        # Check if limit exceeded
        if len(_memory_limits[key]) >= count:
            logger.debug(f"Rate limit exceeded for {key}: {len(_memory_limits[key])}/{count}")
            return False
        
        # Add current request
        _memory_limits[key].append(now)
        return True
        
    except Exception as e:
        logger.error(f"Error checking memory rate limit: {e}")
        return True  # Allow through on error


# Note: For Vercel without Redis, rate limiting is basic but still functional.
# Production users should enable Redis for more robust rate limiting.
