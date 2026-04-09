import json
from fastapi import APIRouter, Query, Depends, Request
from core.security import get_current_user, TokenData
from core.rate_limit import limiter, RATE_LIMITS
from core.redis import get_cache, set_cache, delete_cache
from core.config import REDIS_CACHE_TTL
from services.food import (
    create_food,
    get_all_foods,
    get_food_by_id,
    search_foods_by_name,
    semantic_search_foods,
    update_food,
    delete_food,
    FoodItem,
    FoodResponse,
    FoodListResponse
)

router = APIRouter(
    prefix="/api/food",
    tags=["food"],
    responses={404: {"description": "Not found"}},
)

@router.post("/", response_model=FoodResponse)
@limiter.limit(RATE_LIMITS["food_write"])
async def create_food_endpoint(
    request: Request,
    food: FoodItem,
    created_by: str = Query(None),
    current_user: TokenData = Depends(get_current_user)
):
    """Create a new food item (embeddings auto-generated) - Requires JWT token
    Rate limited: 20 requests per minute"""
    return await create_food(food, current_user.user_id)

@router.get("/", response_model=FoodListResponse)
async def get_all_foods_endpoint(
    current_user: TokenData = Depends(get_current_user)
):
    """Get all food items (cached for 1 hour) - Requires JWT token"""
    from services.food import get_response_hash
    
    cache_key = "food:all"
    
    # Always fetch fresh data from database
    result = await get_all_foods()
    
    # Try to get cached version
    cached = await get_cache(cache_key)
    
    if cached:
        cached_data = FoodListResponse(**json.loads(cached))
        # Compare responses - if different, clear old cache
        if get_response_hash(result.data) != get_response_hash(cached_data.data):
            await delete_cache(cache_key)
    
    # Cache the fresh result
    await set_cache(cache_key, result.model_dump_json(), REDIS_CACHE_TTL)
    
    return result

@router.get("/{food_id}", response_model=FoodResponse)
async def get_food_endpoint(
    food_id: str,
    current_user: TokenData = Depends(get_current_user)
):
    """Get a specific food item by ID (cached for 1 hour) - Requires JWT token"""
    # Create cache key
    cache_key = f"food:{food_id}"
    
    # Try to get from cache
    cached = await get_cache(cache_key)
    if cached:
        return FoodResponse(**json.loads(cached))
    
    # If not in cache, fetch from database
    result = await get_food_by_id(food_id)
    
    # Cache the result
    if result.success:
        await set_cache(cache_key, result.model_dump_json(), REDIS_CACHE_TTL)
    
    return result

@router.get("/search/by-name", response_model=FoodListResponse)
async def search_foods_endpoint(
    name: str = Query(...),
    current_user: TokenData = Depends(get_current_user)
):
    """Search food items by name (exact/partial text match, cached for 1 hour) - Requires JWT token"""
    from services.food import get_response_hash
    
    cache_key = f"food:search:name:{name.lower()}"
    
    # Always fetch fresh data from database
    result = await search_foods_by_name(name)
    
    # Try to get cached version
    cached = await get_cache(cache_key)
    
    if cached:
        cached_data = FoodListResponse(**json.loads(cached))
        # Compare responses - if different, clear old cache
        if get_response_hash(result.data) != get_response_hash(cached_data.data):
            await delete_cache(cache_key)
    
    # Cache the fresh result
    await set_cache(cache_key, result.model_dump_json(), REDIS_CACHE_TTL)
    
    return result

@router.get("/search/semantic", response_model=FoodListResponse)
async def semantic_search_endpoint(
    query: str = Query(...),
    limit: int = Query(10, ge=1, le=50),
    current_user: TokenData = Depends(get_current_user)
):
    """
    Semantic search using AI embeddings (cached for 1 hour) - Requires JWT token.
    Finds foods similar in meaning to your query, even if exact text doesn't match.
    
    Examples:
    - "protein" → Finds chicken, beef, protein bars, etc.
    - "quick breakfast" → Finds fast foods, cereals, fruits
    - "vegetable" → Finds all vegetables and plant-based foods
    
    Returns results ranked by relevance similarity.
    """
    from services.food import get_response_hash
    
    cache_key = f"food:search:semantic:{query.lower()}:{limit}"
    
    # Always fetch fresh data from database
    result = await semantic_search_foods(query, limit)
    
    # Try to get cached version
    cached = await get_cache(cache_key)
    
    if cached:
        cached_data = FoodListResponse(**json.loads(cached))
        # Compare responses - if different, clear old cache
        if get_response_hash(result.data) != get_response_hash(cached_data.data):
            await delete_cache(cache_key)
    
    # Cache the fresh result
    await set_cache(cache_key, result.model_dump_json(), REDIS_CACHE_TTL)
    
    return result

@router.put("/{food_id}", response_model=FoodResponse)
@limiter.limit(RATE_LIMITS["food_write"])
async def update_food_endpoint(
    request: Request,
    food_id: str,
    food: FoodItem,
    current_user: TokenData = Depends(get_current_user)
):
    """Update a food item (embeddings updated automatically) - Requires JWT token
    Rate limited: 20 requests per minute
    Invalidates cache on update"""
    result = await update_food(food_id, food)
    
    # Invalidate related caches
    await delete_cache(f"food:{food_id}")
    await delete_cache("food:all")
    
    return result

@router.delete("/{food_id}", response_model=FoodResponse)
@limiter.limit(RATE_LIMITS["food_write"])
async def delete_food_endpoint(
    request: Request,
    food_id: str,
    current_user: TokenData = Depends(get_current_user)
):
    """Delete a food item - Requires JWT token
    Rate limited: 20 requests per minute
    Invalidates cache on delete"""
    result = await delete_food(food_id)
    
    # Invalidate related caches
    await delete_cache(f"food:{food_id}")
    await delete_cache("food:all")
    
    return result
