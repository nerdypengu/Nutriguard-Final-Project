"""
Bot API endpoints for consumption log operations.
Uses service role key to bypass RLS - accessible to bots only with API key.
"""
from typing import Optional
from fastapi import APIRouter, Query, HTTPException, status
from datetime import date
from services.bot_logs import (
    bot_log_consumption,
    bot_get_user_logs,
    bot_get_user_daily_totals,
    bot_get_today_logs,
    BotConsumptionLog
)
from core.security import verify_bot_token
from pydantic import BaseModel


router = APIRouter(
    prefix="/api/bot/logs",
    tags=["bot_logs"],
    responses={404: {"description": "Not found"}},
)


class BotLogResponse(BaseModel):
    """Response for bot log endpoints"""
    success: bool
    message: str
    data: Optional[dict] = None


class BotLogListResponse(BaseModel):
    """Response for bot log list endpoints"""
    success: bool
    message: str
    data: Optional[list] = None


@router.post("/", response_model=BotLogResponse)
async def bot_log_consumption_endpoint(
    log: BotConsumptionLog,
    authorization: str = Query(...)
):
    """
    Bot: Log food consumption for any user (bypass RLS).
    Requires bot JWT token.
    
    Example:
        POST /api/bot/logs/?authorization=Bearer+{jwt}
        {
            "user_id": "user-uuid",
            "food_name": "Chicken Breast",
            "total_calories": 165,
            "total_protein": 31,
            "total_carbs": 0,
            "total_fat": 3.6
        }
    """
    try:
        # Validate bot JWT token
        token = authorization.replace("Bearer ", "")
        token_data = verify_bot_token(token)
        
        result = await bot_log_consumption(log)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token: {str(e)}"
        )


@router.get("/user/{user_id}", response_model=BotLogListResponse)
async def bot_get_user_logs_endpoint(
    user_id: str,
    limit: int = Query(100),
    authorization: str = Query(...)
):
    """
    Bot: Get consumption logs for a user (bypass RLS).
    Requires bot JWT token.
    """
    try:
        # Validate bot JWT token
        token = authorization.replace("Bearer ", "")
        token_data = verify_bot_token(token)
        
        result = await bot_get_user_logs(user_id, limit)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token: {str(e)}"
        )


@router.get("/user/{user_id}/totals/{target_date}", response_model=BotLogResponse)
async def bot_get_daily_totals_endpoint(
    user_id: str,
    target_date: date,
    authorization: str = Query(...)
):
    """
    Bot: Get daily nutrition totals for a user (bypass RLS).
    Requires bot JWT token.
    """
    try:
        # Validate bot JWT token
        token = authorization.replace("Bearer ", "")
        token_data = verify_bot_token(token)
        
        result = await bot_get_user_daily_totals(user_id, target_date)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token: {str(e)}"
        )


@router.get("/user/{user_id}/today", response_model=BotLogListResponse)
async def bot_get_today_logs_endpoint(
    user_id: str,
    authorization: str = Query(...)
):
    """
    Bot: Get consumption logs for today for a user (bypass RLS).
    Requires bot JWT token.
    
    Example:
        GET /api/bot/logs/user/{user_id}/today?authorization=Bearer+{jwt}
    """
    try:
        # Validate bot JWT token
        token = authorization.replace("Bearer ", "")
        token_data = verify_bot_token(token)
        
        result = await bot_get_today_logs(user_id)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token: {str(e)}"
        )
