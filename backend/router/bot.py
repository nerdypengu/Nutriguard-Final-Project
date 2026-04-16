"""
Bot API endpoints for Discord bot verification and authorization.
"""
import json
from fastapi import APIRouter
from services.bot import verify_discord_user, BotVerificationResponse
from core.redis import get_cache, set_cache, delete_cache
from core.config import REDIS_CACHE_TTL

router = APIRouter(
    prefix="/api/bot",
    tags=["bot"],
    responses={404: {"description": "Not found"}},
)


@router.get("/verify/{discord_id}", response_model=BotVerificationResponse)
async def verify_bot_access(discord_id: str):
    """
    Verify if a Discord user is authorized to use the bot.
    Results are cached for 1 hour to reduce database queries.
    
    This endpoint checks:
    1. If the Discord user exists in the database (discord_id)
    2. If their subscription is active (is_subscribed = true)
    3. If authorized, returns their user_id and target_calories
    
    Args:
        discord_id (str): The Discord user ID to verify
        
    Returns:
        BotVerificationResponse: Authorization status with user context if authorized
        
    Example:
        GET /api/bot/verify/123456789
        Response:
        {
            "is_authorized": true,
            "reason": "Success",
            "user_context": {
                "user_id": "550e8400-e29b-41d4-a716-446655440000",
                "target_calories": 2500
            }
        }
    """

    
    # Create cache key
    cache_key = f"bot:verify:{discord_id}"
    
    # Always fetch fresh data
    result = await verify_discord_user(discord_id)
    
    # Try to get cached version
    cached = await get_cache(cache_key)
    
    if cached:
        cached_data = BotVerificationResponse(**json.loads(cached))
        # Compare responses using hash - if different, clear old cache
        result_hash = str(hash((result.is_authorized, str(result.user_context))))
        cached_hash = str(hash((cached_data.is_authorized, str(cached_data.user_context))))
        if result_hash != cached_hash:
            await delete_cache(cache_key)
    
    # Cache the fresh result
    await set_cache(cache_key, result.model_dump_json(), REDIS_CACHE_TTL)
    
    return result
