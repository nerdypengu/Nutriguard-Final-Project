import json
from fastapi import APIRouter, Query, Depends, Request
from datetime import date
from core.security import get_current_user, TokenData
from core.rate_limit import limiter, RATE_LIMITS
from core.redis import get_cache, set_cache, delete_cache
from core.config import REDIS_CACHE_TTL
from services.consumption_logs import (
    log_consumption,
    get_user_logs,
    get_user_logs_by_date,
    get_daily_totals,
    update_log,
    delete_log,
    ConsumptionLog,
    LogResponse,
    LogListResponse
)

router = APIRouter(
    prefix="/api/logs",
    tags=["consumption_logs"],
    responses={404: {"description": "Not found"}},
)

@router.post("/", response_model=LogResponse)
@limiter.limit(RATE_LIMITS["general"])
async def log_consumption_endpoint(
    request: Request,
    log: ConsumptionLog,
    current_user: TokenData = Depends(get_current_user)
):
    """Log food consumption - Requires JWT token
    Rate limited: 100 requests per minute
    Invalidates daily totals cache on new log"""
    result = await log_consumption(log)
    
    # Invalidate daily totals cache
    log_date = log.logged_at.split('T')[0] if log.logged_at else date.today().isoformat()
    await delete_cache(f"logs:totals:{log.user_id}:{log_date}")
    
    return result

@router.get("/user/{user_id}", response_model=LogListResponse)
async def get_user_logs_endpoint(
    user_id: str,
    limit: int = Query(100),
    current_user: TokenData = Depends(get_current_user)
):
    """Get all consumption logs for a user (cached for 1 hour) - Requires JWT token"""
    from services.food import get_response_hash
    
    # Users can only view their own logs
    if current_user.user_id != user_id:
        return LogListResponse(
            success=False,
            message="Unauthorized: Can only view your own logs"
        )
    
    cache_key = f"logs:user:{user_id}:limit:{limit}"
    
    # Always fetch fresh data
    result = await get_user_logs(user_id, limit)
    
    # Try to get cached version
    cached = await get_cache(cache_key)
    
    if cached:
        cached_data = LogListResponse(**json.loads(cached))
        # Compare responses - if different, clear old cache
        if get_response_hash(result.data) != get_response_hash(cached_data.data):
            await delete_cache(cache_key)
    
    # Cache the fresh result
    await set_cache(cache_key, result.model_dump_json(), REDIS_CACHE_TTL)
    
    return result

@router.get("/user/{user_id}/date/{target_date}", response_model=LogListResponse)
async def get_logs_by_date_endpoint(
    user_id: str,
    target_date: date,
    current_user: TokenData = Depends(get_current_user)
):
    """Get consumption logs for a specific date (cached for 1 hour) - Requires JWT token"""
    from services.food import get_response_hash
    
    # Users can only view their own logs
    if current_user.user_id != user_id:
        return LogListResponse(
            success=False,
            message="Unauthorized: Can only view your own logs"
        )
    
    cache_key = f"logs:user:{user_id}:date:{target_date}"
    
    # Always fetch fresh data
    result = await get_user_logs_by_date(user_id, target_date)
    
    # Try to get cached version
    cached = await get_cache(cache_key)
    
    if cached:
        cached_data = LogListResponse(**json.loads(cached))
        # Compare responses - if different, clear old cache
        if get_response_hash(result.data) != get_response_hash(cached_data.data):
            await delete_cache(cache_key)
    
    # Cache the fresh result
    await set_cache(cache_key, result.model_dump_json(), REDIS_CACHE_TTL)
    
    return result

@router.get("/user/{user_id}/totals/{target_date}", response_model=LogResponse)
async def get_daily_totals_endpoint(
    user_id: str,
    target_date: date,
    current_user: TokenData = Depends(get_current_user)
):
    """Get daily nutrition totals (cached for 1 hour) - Requires JWT token"""
    # Users can only view their own totals
    if current_user.user_id != user_id:
        return LogResponse(
            success=False,
            message="Unauthorized: Can only view your own totals"
        )
    
    cache_key = f"logs:totals:{user_id}:{target_date}"
    
    # Try to get from cache
    cached = await get_cache(cache_key)
    if cached:
        return LogResponse(**json.loads(cached))
    
    # If not in cache, fetch from database
    result = await get_daily_totals(user_id, target_date)
    
    # Cache the result
    await set_cache(cache_key, result.model_dump_json(), REDIS_CACHE_TTL)
    
    return result

@router.put("/{log_id}", response_model=LogResponse)
@limiter.limit(RATE_LIMITS["general"])
async def update_log_endpoint(
    request: Request,
    log_id: str,
    log: ConsumptionLog,
    current_user: TokenData = Depends(get_current_user)
):
    """Update a consumption log - Requires JWT token
    Rate limited: 100 requests per minute
    Invalidates cache on update"""
    result = await update_log(log_id, log)
    
    # Invalidate related caches
    log_date = log.logged_at.split('T')[0] if log.logged_at else date.today().isoformat()
    await delete_cache(f"logs:totals:{log.user_id}:{log_date}")
    
    return result

@router.delete("/{log_id}", response_model=LogResponse)
@limiter.limit(RATE_LIMITS["general"])
async def delete_log_endpoint(
    request: Request,
    log_id: str,
    current_user: TokenData = Depends(get_current_user)
):
    """Delete a consumption log - Requires JWT token
    Rate limited: 100 requests per minute
    Invalidates cache on delete"""
    return await delete_log(log_id)
