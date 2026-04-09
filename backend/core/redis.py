"""
Redis client initialization and utilities for NutriGuard Backend.
Used for caching, rate limiting, and session management.
Includes fallback for production environments without Redis (e.g., Vercel).
"""
import redis.asyncio as redis
from typing import Optional
from core.config import REDIS_URL
import logging

logger = logging.getLogger(__name__)

# Redis client instance (singleton)
_redis_client: Optional[redis.Redis] = None
_redis_available: bool = False

# In-memory fallback cache (basic, no TTL enforcement)
_fallback_cache: dict = {}


async def get_redis_client() -> Optional[redis.Redis]:
    """
    Get or create Redis client instance with fallback.
    
    Returns:
        redis.Redis: Async Redis client, or None if unavailable
    """
    global _redis_client, _redis_available
    
    if _redis_client is None and not _redis_available:
        try:
            _redis_client = await redis.from_url(REDIS_URL, encoding="utf8", decode_responses=True)
            # Test connection
            await _redis_client.ping()
            _redis_available = True
            logger.info("✓ Redis connection successful")
        except Exception as e:
            logger.warning(f"✗ Redis unavailable, using fallback cache: {e}")
            _redis_available = False
            _redis_client = None
    
    return _redis_client if _redis_available else None


async def close_redis():
    """Close Redis connection safely"""
    global _redis_client, _redis_available
    if _redis_client:
        try:
            await _redis_client.close()
        except Exception as e:
            logger.error(f"Error closing Redis: {e}")
        finally:
            _redis_client = None
            _redis_available = False


async def set_cache(key: str, value: str, ttl: int = 3600) -> bool:
    """
    Set a value in cache (Redis or fallback).
    
    Args:
        key (str): Cache key
        value (str): Value to cache (as JSON string)
        ttl (int): Time to live in seconds (default: 1 hour)
        
    Returns:
        bool: True if set in Redis, False if using fallback
    """
    try:
        client = await get_redis_client()
        if client:
            await client.setex(key, ttl, value)
            return True
    except Exception as e:
        logger.warning(f"Failed to set Redis cache for {key}: {e}")
    
    # Fallback to in-memory cache
    _fallback_cache[key] = value
    return False


async def get_cache(key: str) -> Optional[str]:
    """
    Get a value from cache (Redis or fallback).
    
    Args:
        key (str): Cache key
        
    Returns:
        Optional[str]: Cached value or None if not found/expired
    """
    try:
        client = await get_redis_client()
        if client:
            value = await client.get(key)
            if value is not None:
                return value
    except Exception as e:
        logger.warning(f"Failed to get Redis cache for {key}: {e}")
    
    # Fallback to in-memory cache
    return _fallback_cache.get(key)


async def delete_cache(key: str) -> None:
    """
    Delete a key from Redis cache.
    
    Args:
        key (str): Cache key to delete
    """
    client = await get_redis_client()
    await client.delete(key)


async def clear_user_cache(user_id: str) -> None:
    """
    Clear all cache entries for a specific user.
    Uses pattern matching with user_id prefix.
    
    Args:
        user_id (str): User ID to clear cache for
    """
    client = await get_redis_client()
    pattern = f"user:{user_id}:*"
    keys = await client.keys(pattern)
    if keys:
        await client.delete(*keys)
