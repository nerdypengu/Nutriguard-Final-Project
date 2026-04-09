"""
Bot verification service for Discord bot authorization checks.
Verifies if a Discord user is authorized to use the bot.
"""
from typing import Optional
from pydantic import BaseModel
from core.supabase import get_supabase_service_client


class UserContext(BaseModel):
    """User context returned for authorized users"""
    user_id: str
    target_calories: Optional[int] = None


class BotVerificationResponse(BaseModel):
    """Response schema for bot verification endpoint"""
    is_authorized: bool
    reason: str
    user_context: Optional[UserContext] = None


async def verify_discord_user(discord_id: str) -> BotVerificationResponse:
    """
    Verify if a Discord user is authorized to use the bot.
    
    Steps:
    1. Look up discord_id in nutriguard.users
    2. If not found, return unauthorized
    3. If found, check is_subscribed boolean
    4. If not subscribed, return unauthorized
    5. If subscribed, LEFT JOIN with user_preferences to get target_calories
    6. Return authorized with user context
    
    Args:
        discord_id (str): The Discord user ID to verify
        
    Returns:
        BotVerificationResponse: Authorization status with user context if authorized
    """
    try:
        # Strip whitespace from discord_id
        discord_id = discord_id.strip()
        
        supabase = get_supabase_service_client()
        
        # Step 1 & 2: Query user by discord_id
        try:
            user_response = (
                supabase.schema("nutriguard").table("users")
                .select("id, is_subscribed")
                .eq("discord_id", str(discord_id))
                .single()
                .execute()
            )
            user = user_response.data
        except Exception as single_error:
            # If not found, user is None
            if "not found" in str(single_error).lower() or "0 rows" in str(single_error).lower():
                user = None
            else:
                raise
        
        # User not found
        if not user:
            print(f"Discord user {discord_id} not found in database")
            return BotVerificationResponse(
                is_authorized=False,
                reason="I don't recognize this Discord account. Please link your account at nutriguard.com!",
                user_context=None
            )
        
        # Step 3: Check subscription status
        if not user.get("is_subscribed", False):
            return BotVerificationResponse(
                is_authorized=False,
                reason="Your subscription is not active. Please subscribe at nutriguard.com!",
                user_context=None
            )
        
        # Step 4 & 5: User exists and is subscribed, get preferences
        user_id = user["id"]
        
        try:
            preferences_response = (
                supabase.schema("nutriguard").table("user_preferences")
                .select("target_calories")
                .eq("user_id", user_id)
                .single()
                .execute()
            )
            preferences = preferences_response.data
        except Exception as pref_error:
            # If preferences not found, set to None
            if "not found" in str(pref_error).lower() or "0 rows" in str(pref_error).lower():
                preferences = None
            else:
                raise
        
        preferences = preferences_response.data
        target_calories = preferences.get("target_calories") if preferences else None
        
        # Step 6: Return authorized with user context
        return BotVerificationResponse(
            is_authorized=True,
            reason="Success",
            user_context=UserContext(
                user_id=user_id,
                target_calories=target_calories
            )
        )
        
    except Exception as e:
        # If user not found (single() throws error when no results)
        if "not found" in str(e).lower():
            return BotVerificationResponse(
                is_authorized=False,
                reason="I don't recognize this Discord account. Please link your account at nutriguard.com!",
                user_context=None
            )
        
        # Unexpected error
        print(f"ERROR verifying Discord user {discord_id}: {type(e).__name__} - {str(e)}")
        import traceback
        traceback.print_exc()
        return BotVerificationResponse(
            is_authorized=False,
            reason="An error occurred while verifying your account. Please try again later.",
            user_context=None
        )
