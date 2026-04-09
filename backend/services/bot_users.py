"""
Bot users service - uses service role key to bypass RLS.
Retrieves user data and preferences for bot operations.
"""
from typing import Optional
from pydantic import BaseModel
from core.supabase import supabase_service_client


class BotUserPreferences(BaseModel):
    """Response model for user preferences"""
    success: bool
    message: str
    data: Optional[dict] = None


async def get_bot_user_preferences(user_id: str) -> BotUserPreferences:
    """Fetch user preferences (uses service role - no RLS)"""
    try:
        response = supabase_service_client.schema("nutriguard").table("user_preferences")\
            .select("*")\
            .eq("user_id", user_id)\
            .single()\
            .execute()
        
        if response.data:
            return BotUserPreferences(
                success=True,
                message="User preferences retrieved successfully",
                data=response.data
            )
        else:
            return BotUserPreferences(
                success=False,
                message="User preferences not found"
            )
    except Exception as e:
        if "not found" in str(e).lower() or "0 rows" in str(e).lower():
            return BotUserPreferences(
                success=False,
                message="User preferences not found"
            )
        return BotUserPreferences(
            success=False,
            message=f"Error fetching user preferences: {str(e)}"
        )
