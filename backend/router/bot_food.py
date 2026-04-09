"""
Bot API endpoints for food operations.
Uses service role key to bypass RLS - accessible to bots only with API key.
"""
import json
from typing import Optional
from fastapi import APIRouter, Query, HTTPException, status
from services.bot_food import get_bot_food, search_bot_food_by_name, semantic_search_bot_food
from core.security import verify_bot_token
from pydantic import BaseModel

router = APIRouter(
    prefix="/api/bot/food",
    tags=["bot_food"],
    responses={404: {"description": "Not found"}},
)


class BotFoodResponse(BaseModel):
    """Response for bot food endpoints"""
    success: bool
    message: str
    data: Optional[dict] = None


class BotFoodListResponse(BaseModel):
    """Response for bot food list endpoints"""
    success: bool
    message: str
    data: Optional[list] = None


@router.get("/search/by-name", response_model=BotFoodListResponse)
async def bot_search_foods_by_name(
    name: str = Query(...),
    authorization: str = Query(...)
):
    """
    Bot: Search food items by name (bypass RLS).
    Requires bot JWT token.
    
    Example: /api/bot/food/search/by-name?name=chicken&authorization=Bearer+{jwt}
    """
    try:
        # Validate bot JWT token
        token = authorization.replace("Bearer ", "")
        token_data = verify_bot_token(token)
        
        result = await search_bot_food_by_name(name)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token: {str(e)}"
        )


@router.get("/search/semantic", response_model=BotFoodListResponse)
async def bot_semantic_search_food(
    query: str = Query(...),
    limit: int = Query(10, ge=1, le=50),
    authorization: str = Query(...)
):
    """
    Bot: Semantic search food items (bypass RLS).
    Requires bot JWT token.
    """
    try:
        # Validate bot JWT token
        token = authorization.replace("Bearer ", "")
        token_data = verify_bot_token(token)
        
        result = await semantic_search_bot_food(query, limit)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token: {str(e)}"
        )


@router.get("/{food_id}", response_model=BotFoodResponse)
async def bot_get_food(
    food_id: str,
    authorization: str = Query(...)
):
    """
    Bot: Get a specific food item (bypass RLS).
    Requires bot JWT token.
    """
    try:
        # Validate bot JWT token
        token = authorization.replace("Bearer ", "")
        token_data = verify_bot_token(token)
        
        result = await get_bot_food(food_id)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token: {str(e)}"
        )
