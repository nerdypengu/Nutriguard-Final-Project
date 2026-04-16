import json
from fastapi import APIRouter, Depends, Request
from datetime import date
from core.security import get_current_user, TokenData
from core.rate_limit import limiter, RATE_LIMITS
from core.redis import get_cache, set_cache, delete_cache
from core.config import REDIS_CACHE_TTL
from services.meal_plans import (
    create_meal_plan,
    get_meal_plan,
    get_user_meal_plans,
    get_meal_plans_by_date,
    update_meal_plan,
    update_meal_plan_status,
    delete_meal_plan,
    MealPlan,
    PlanResponse,
    PlanListResponse
)

router = APIRouter(
    prefix="/api/meal-plans",
    tags=["meal_plans"],
    responses={404: {"description": "Not found"}},
)

@router.post("/", response_model=PlanResponse)
@limiter.limit(RATE_LIMITS["general"])
async def create_meal_plan_endpoint(
    request: Request,
    plan: MealPlan,
    current_user: TokenData = Depends(get_current_user)
):
    """Create a new meal plan - Requires JWT token
    Rate limited: 100 requests per minute"""
    plan.user_id = current_user.user_id
    result = await create_meal_plan(plan)
    
    # Invalidate user's meal plan cache
    await delete_cache(f"meals:user:{current_user.user_id}")
    
    return result

@router.get("/{plan_id}", response_model=PlanResponse)
async def get_meal_plan_endpoint(
    plan_id: str,
    current_user: TokenData = Depends(get_current_user)
):
    """Get a meal plan by ID (cached for 1 hour) - Requires JWT token"""
    cache_key = f"meals:plan:{plan_id}"
    
    # Try to get from cache
    cached = await get_cache(cache_key)
    if cached:
        return PlanResponse(**json.loads(cached))
    
    # If not in cache, fetch from database
    result = await get_meal_plan(plan_id)
    
    # Cache the result
    if result.success:
        await set_cache(cache_key, result.model_dump_json(), REDIS_CACHE_TTL)
    
    return result

@router.get("/user/{user_id}", response_model=PlanListResponse)
async def get_user_meal_plans_endpoint(
    user_id: str,
    current_user: TokenData = Depends(get_current_user)
):
    """Get all meal plans for a user (cached for 1 hour) - Requires JWT token"""
    # Users can only view their own meal plans
    if current_user.user_id != user_id:
        return PlanListResponse(
            success=False,
            message="Unauthorized: Can only view your own meal plans"
        )
    
    cache_key = f"meals:user:{user_id}"
    
    # Fetch from database (bypassing cache for immediate updates during development)
    result = await get_user_meal_plans(user_id)
    
    # Cache the result for performance (5 mins)
    await set_cache(cache_key, result.model_dump_json(), 300)
    
    return result

@router.get("/user/{user_id}/date/{target_date}", response_model=PlanListResponse)
async def get_meal_plans_by_date_endpoint(
    user_id: str,
    target_date: date,
    current_user: TokenData = Depends(get_current_user)
):
    """Get meal plans for a specific date (cached for 1 hour) - Requires JWT token"""
    # Users can only view their own meal plans
    if current_user.user_id != user_id:
        return PlanListResponse(
            success=False,
            message="Unauthorized: Can only view your own meal plans"
        )
    
    cache_key = f"meals:user:{user_id}:date:{target_date}"
    
    # Try to get from cache
    cached = await get_cache(cache_key)
    if cached:
        return PlanListResponse(**json.loads(cached))
    
    # If not in cache, fetch from database
    result = await get_meal_plans_by_date(user_id, target_date)
    
    # Cache the result
    await set_cache(cache_key, result.model_dump_json(), REDIS_CACHE_TTL)
    
    return result


@router.get("/user/{user_id}/current", response_model=PlanListResponse)
async def get_current_meal_plan_endpoint(
    user_id: str,
    current_user: TokenData = Depends(get_current_user)
):
    """Get today's meal plans for a user (convenience endpoint for bots) - Requires JWT token
    
    This is a convenience endpoint that automatically uses today's date.
    Useful for n8n workflows and bot integrations.
    """
    # Users can only view their own meal plans
    if current_user.user_id != user_id:
        return PlanListResponse(
            success=False,
            message="Unauthorized: Can only view your own meal plans"
        )
    
    today = date.today()
    cache_key = f"meals:user:{user_id}:date:{today}"
    
    # Fetch fresh from database (skip cache for current day to ensure immediate updates)
    result = await get_meal_plans_by_date(user_id, today)
    
    # Cache the result for other callers, but always return fresh data here
    await set_cache(cache_key, result.model_dump_json(), 300) # Lower TTL to 5 mins for today
    
    return result

@router.put("/{plan_id}", response_model=PlanResponse)
@limiter.limit(RATE_LIMITS["general"])
async def update_meal_plan_endpoint(
    request: Request,
    plan_id: str,
    plan: MealPlan,
    current_user: TokenData = Depends(get_current_user)
):
    """Update a meal plan - Requires JWT token
    Rate limited: 100 requests per minute
    Invalidates cache on update"""
    plan.user_id = current_user.user_id
    result = await update_meal_plan(plan_id, plan)
    
    # Invalidate related caches
    await delete_cache(f"meals:plan:{plan_id}")
    await delete_cache(f"meals:user:{current_user.user_id}")
    
    return result

@router.patch("/{plan_id}/status", response_model=PlanResponse)
@limiter.limit(RATE_LIMITS["general"])
async def update_meal_plan_status_endpoint(
    request: Request,
    plan_id: str,
    status: str,
    current_user: TokenData = Depends(get_current_user)
):
    """Update meal plan status - Requires JWT token
    Rate limited: 100 requests per minute
    Invalidates cache on update"""
    result = await update_meal_plan_status(plan_id, status)
    
    # Invalidate related caches
    await delete_cache(f"meals:plan:{plan_id}")
    
    return result

@router.delete("/{plan_id}", response_model=PlanResponse)
@limiter.limit(RATE_LIMITS["general"])
async def delete_meal_plan_endpoint(
    request: Request,
    plan_id: str,
    current_user: TokenData = Depends(get_current_user)
):
    """Delete a meal plan - Requires JWT token
    Rate limited: 100 requests per minute
    Invalidates cache on delete"""
    result = await delete_meal_plan(plan_id)
    
    # Invalidate related caches
    await delete_cache(f"meals:plan:{plan_id}")
    await delete_cache(f"meals:user:{current_user.user_id}")
    
    return result
