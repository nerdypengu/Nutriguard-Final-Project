"""
Bot API endpoints for user operations.
Uses service role key to bypass RLS - accessible to bots only with API key.
"""
from typing import Optional
from fastapi import APIRouter, Query, HTTPException, status
from services.bot_users import get_bot_user_preferences
from core.security import verify_bot_token
from pydantic import BaseModel


router = APIRouter(
    prefix="/api/bot/users",
    tags=["bot_users"],
    responses={404: {"description": "Not found"}},
)


class BotUserResponse(BaseModel):
    """Response for bot user endpoints"""
    success: bool
    message: str
    data: Optional[dict] = None


@router.get("/{user_id}/preferences", response_model=BotUserResponse)
async def bot_get_user_preferences(
    user_id: str,
    authorization: str = Query(...)
):
    """
    Bot: Get user preferences (bypass RLS).
    Requires bot JWT token.
    
    Returns user's diet type, target macros, and preferred meal generation day.
    
    Example: /api/bot/users/user-uuid/preferences?authorization=Bearer+{jwt}
    """
    try:
        # Validate bot JWT token
        token = authorization.replace("Bearer ", "")
        verify_bot_token(token)
        
        result = await get_bot_user_preferences(user_id)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token: {str(e)}"
        )
