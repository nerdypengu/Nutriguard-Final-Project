"""
Bot API endpoints for meal plan operations.
Uses service role key to bypass RLS - accessible to bots only with API key.
"""
from typing import Optional
from fastapi import APIRouter, Query, HTTPException, status
from datetime import date
from services.bot_meal_plans import (
    get_bot_user_meal_plans,
    get_bot_user_current_meal_plan,
    get_bot_user_meal_plans_by_date,
    create_bot_meal_plan,
    update_bot_meal_plan,
    BotMealPlan
)
from core.security import verify_bot_token
from pydantic import BaseModel


router = APIRouter(
    prefix="/api/bot/meal-plans",
    tags=["bot_meal_plans"],
    responses={404: {"description": "Not found"}},
)


class BotMealPlanResponse(BaseModel):
    """Response for bot meal plan endpoints"""
    success: bool
    message: str
    data: Optional[dict] = None


class BotMealPlanListResponse(BaseModel):
    """Response for bot meal plan list endpoints"""
    success: bool
    message: str
    data: Optional[list] = None


@router.get("/user/{user_id}", response_model=BotMealPlanListResponse)
async def bot_get_user_meal_plans(
    user_id: str,
    authorization: str = Query(...)
):
    """
    Bot: Get all meal plans for a user (bypass RLS).
    Requires bot JWT token.
    """
    try:
        # Validate bot JWT token
        token = authorization.replace("Bearer ", "")
        token_data = verify_bot_token(token)
        
        result = await get_bot_user_meal_plans(user_id)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token: {str(e)}"
        )


@router.get("/user/{user_id}/current", response_model=BotMealPlanListResponse)
async def bot_get_user_current_meal_plan(
    user_id: str,
    authorization: str = Query(...)
):
    """
    Bot: Get today's meal plans for a user (bypass RLS).
    Requires bot JWT token.
    """
    try:
        # Validate bot JWT token
        token = authorization.replace("Bearer ", "")
        token_data = verify_bot_token(token)
        
        result = await get_bot_user_current_meal_plan(user_id)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token: {str(e)}"
        )


@router.get("/user/{user_id}/date/{target_date}", response_model=BotMealPlanListResponse)
async def bot_get_user_meal_plans_by_date(
    user_id: str,
    target_date: date,
    authorization: str = Query(...)
):
    """
    Bot: Get meal plans for a specific date (bypass RLS).
    Requires bot JWT token.
    """
    try:
        # Validate bot JWT token
        token = authorization.replace("Bearer ", "")
        token_data = verify_bot_token(token)
        
        result = await get_bot_user_meal_plans_by_date(user_id, target_date)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token: {str(e)}"
        )


@router.post("/", response_model=BotMealPlanResponse)
async def bot_create_meal_plan(
    plan: BotMealPlan,
    authorization: str = Query(...)
):
    """
    Bot: Create a meal plan for a user (bypass RLS).
    Requires bot JWT token.
    
    Example:
        POST /api/bot/meal-plans/?authorization=Bearer+{jwt}
        {
            "user_id": "user-uuid",
            "meal_name": "Breakfast",
            "total_calories": 500,
            "total_protein": 20,
            "total_carbs": 60,
            "total_fat": 15,
            "planned_for_date": "2026-04-08",
            "status": "Planned"
        }
    """
    try:
        # Validate bot JWT token
        token = authorization.replace("Bearer ", "")
        token_data = verify_bot_token(token)
        
        result = await create_bot_meal_plan(plan)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token: {str(e)}"
        )


@router.patch("/{plan_id}", response_model=BotMealPlanResponse)
async def bot_update_meal_plan(
    plan_id: str,
    plan_update: dict,
    authorization: str = Query(...)
):
    """
    Bot: Update a meal plan (bypass RLS).
    Requires bot JWT token.
    
    Example:
        PATCH /api/bot/meal-plans/plan-uuid?authorization=Bearer+{jwt}
        {
            "total_calories": 550,
            "status": "Completed"
        }
    """
    try:
        # Validate bot JWT token
        token = authorization.replace("Bearer ", "")
        token_data = verify_bot_token(token)
        
        result = await update_bot_meal_plan(plan_id, plan_update)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token: {str(e)}"
        )
