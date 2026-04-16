import json
from fastapi import APIRouter, Depends, Request
from core.security import get_current_user, TokenData
from core.rate_limit import limiter, RATE_LIMITS
from core.redis import get_cache, set_cache, delete_cache
from core.config import REDIS_CACHE_TTL
from services.users import (
    create_user,
    get_user_by_id,
    get_user_by_email,
    get_all_users,
    update_user,
    delete_user,
    create_user_preferences,
    get_user_preferences,
    update_user_preferences,
    delete_user_preferences,

    UserPreferences,
    UserPreferencesInput,
    UserResponse,
    UserListResponse
)

router = APIRouter(
    prefix="/api/users",
    tags=["users"],
    responses={404: {"description": "Not found"}},
)

# User Profile Endpoints

@router.post("/", response_model=UserResponse)
@limiter.limit(RATE_LIMITS["general"])
async def create_user_endpoint(
    request: Request,
    email: str,
    discord_id: str = None,
    discord_username: str = None
):
    """Create a new user profile
    Rate limited: 100 requests per minute"""
    return await create_user(email, discord_id, discord_username)

@router.get("/", response_model=UserListResponse)
async def get_all_users_endpoint(current_user: TokenData = Depends(get_current_user)):
    """Get all users (cached for 1 hour) - Requires JWT token"""
    cache_key = "users:all"
    
    # Try to get from cache
    cached = await get_cache(cache_key)
    if cached:
        return UserListResponse(**json.loads(cached))
    
    # If not in cache, fetch from database
    result = await get_all_users()
    
    # Cache the result
    await set_cache(cache_key, result.model_dump_json(), REDIS_CACHE_TTL)
    
    return result

@router.get("/{user_id}", response_model=UserResponse)
async def get_user_endpoint(
    user_id: str,
    current_user: TokenData = Depends(get_current_user)
):
    """Get a user by ID (cached for 1 hour) - Requires JWT token"""
    cache_key = f"user:{user_id}"
    
    # Try to get from cache
    cached = await get_cache(cache_key)
    if cached:
        return UserResponse(**json.loads(cached))
    
    # If not in cache, fetch from database
    result = await get_user_by_id(user_id)
    
    # Cache the result
    if result.success:
        await set_cache(cache_key, result.model_dump_json(), REDIS_CACHE_TTL)
    
    return result

@router.get("/email/{email}", response_model=UserResponse)
async def get_user_by_email_endpoint(
    email: str,
    current_user: TokenData = Depends(get_current_user)
):
    """Get a user by email (cached for 1 hour) - Requires JWT token"""
    cache_key = f"user:email:{email.lower()}"
    
    # Try to get from cache
    cached = await get_cache(cache_key)
    if cached:
        return UserResponse(**json.loads(cached))
    
    # If not in cache, fetch from database
    result = await get_user_by_email(email)
    
    # Cache the result
    if result.success:
        await set_cache(cache_key, result.model_dump_json(), REDIS_CACHE_TTL)
    
    return result

@router.put("/{user_id}", response_model=UserResponse)
@limiter.limit(RATE_LIMITS["general"])
async def update_user_endpoint(
    request: Request,
    user_id: str,
    current_user: TokenData = Depends(get_current_user),
    discord_id: str = None,
    discord_username: str = None,
    is_subscribed: bool = None
):
    """Update a user profile - Requires JWT token
    Rate limited: 100 requests per minute
    Invalidates cache on update"""
    result = await update_user(user_id, discord_id, discord_username, is_subscribed)
    
    # Invalidate related caches
    await delete_cache(f"user:{user_id}")
    await delete_cache("users:all")
    
    return result

@router.delete("/{user_id}", response_model=UserResponse)
@limiter.limit(RATE_LIMITS["general"])
async def delete_user_endpoint(
    request: Request,
    user_id: str,
    current_user: TokenData = Depends(get_current_user)
):
    """Delete a user - Requires JWT token
    Rate limited: 100 requests per minute
    Invalidates cache on delete"""
    result = await delete_user(user_id)
    
    # Invalidate related caches
    await delete_cache(f"user:{user_id}")
    await delete_cache(f"user:preferences:{user_id}")
    await delete_cache("users:all")
    
    return result

# User Preferences Endpoints

@router.post("/{user_id}/preferences", response_model=UserResponse)
@limiter.limit(RATE_LIMITS["general"])
async def create_preferences_endpoint(
    request: Request,
    user_id: str,
    preferences: UserPreferencesInput,
    current_user: TokenData = Depends(get_current_user)
):
    """Create user preferences - Requires JWT token
    Rate limited: 100 requests per minute
    Invalidates cache on creation
    
    Request body should include:
    - diet_type (optional, defaults to "Standard")
    - target_calories (required)
    - target_protein_g (required)
    - target_carbs_g (required)
    - target_fat_g (required)
    - preferred_generation_day (optional, defaults to "Sunday")
    """
    # Convert input to full UserPreferences with user_id from path
    full_preferences = UserPreferences(
        user_id=user_id,
        diet_type=preferences.diet_type,
        target_calories=preferences.target_calories,
        target_protein_g=preferences.target_protein_g,
        target_carbs_g=preferences.target_carbs_g,
        target_fat_g=preferences.target_fat_g,
        preferred_generation_day=preferences.preferred_generation_day
    )
    result = await create_user_preferences(full_preferences)
    
    # Invalidate related caches
    await delete_cache(f"user:preferences:{user_id}")
    
    return result

@router.get("/{user_id}/preferences", response_model=UserResponse)
async def get_preferences_endpoint(
    user_id: str,
    current_user: TokenData = Depends(get_current_user)
):
    """Get user preferences (cached for 1 hour) - Requires JWT token"""
    cache_key = f"user:preferences:{user_id}"
    
    # Try to get from cache
    cached = await get_cache(cache_key)
    if cached:
        return UserResponse(**json.loads(cached))
    
    # If not in cache, fetch from database
    result = await get_user_preferences(user_id)
    
    # Cache the result
    if result.success:
        await set_cache(cache_key, result.model_dump_json(), REDIS_CACHE_TTL)
    
    return result

@router.put("/{user_id}/preferences", response_model=UserResponse)
@limiter.limit(RATE_LIMITS["general"])
async def update_preferences_endpoint(
    request: Request,
    user_id: str,
    preferences: UserPreferencesInput,
    current_user: TokenData = Depends(get_current_user)
):
    """Update user preferences - Requires JWT token
    Rate limited: 100 requests per minute
    Invalidates cache on update"""
    # Convert input to full UserPreferences with user_id from path
    full_preferences = UserPreferences(
        user_id=user_id,
        diet_type=preferences.diet_type,
        target_calories=preferences.target_calories,
        target_protein_g=preferences.target_protein_g,
        target_carbs_g=preferences.target_carbs_g,
        target_fat_g=preferences.target_fat_g,
        preferred_generation_day=preferences.preferred_generation_day
    )
    result = await update_user_preferences(user_id, full_preferences)
    
    # Invalidate related cache
    await delete_cache(f"user:preferences:{user_id}")
    
    return result

@router.delete("/{user_id}/preferences", response_model=UserResponse)
@limiter.limit(RATE_LIMITS["general"])
async def delete_preferences_endpoint(
    request: Request,
    user_id: str,
    current_user: TokenData = Depends(get_current_user)
):
    """Delete user preferences - Requires JWT token
    Rate limited: 100 requests per minute
    Invalidates cache on delete"""
    result = await delete_user_preferences(user_id)
    
    # Invalidate related cache
    await delete_cache(f"user:preferences:{user_id}")
    
    return result
