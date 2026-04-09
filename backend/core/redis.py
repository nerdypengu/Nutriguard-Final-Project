"""
Redis client initialization and utilities for NutriGuard Backend.
Used for caching, rate limiting, and session management.
"""
import redis.asyncio as redis
from typing import Optional
from core.config import REDIS_URL

# Redis client instance (singleton)
_redis_client: Optional[redis.Redis] = None


async def get_redis_client() -> redis.Redis:
    """
    Get or create Redis client instance.
    
    Returns:
        redis.Redis: Async Redis client
    """
    global _redis_client
    
    if _redis_client is None:
        _redis_client = await redis.from_url(REDIS_URL, encoding="utf8", decode_responses=True)
    
    return _redis_client


async def close_redis():
    """Close Redis connection"""
    global _redis_client
    if _redis_client:
        await _redis_client.close()
        _redis_client = None


async def set_cache(key: str, value: str, ttl: int = 3600) -> None:
    """
    Set a value in Redis cache with TTL.
    
    Args:
        key (str): Cache key
        value (str): Value to cache (as JSON string)
        ttl (int): Time to live in seconds (default: 1 hour)
    """
    client = await get_redis_client()
    await client.setex(key, ttl, value)


async def get_cache(key: str) -> Optional[str]:
    """
    Get a value from Redis cache.
    
    Args:
        key (str): Cache key
        
    Returns:
        Optional[str]: Cached value or None if not found/expired
    """
    client = await get_redis_client()
    return await client.get(key)


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
