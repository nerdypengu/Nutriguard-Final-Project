"""
Bot consumption logs service - uses service role key to bypass RLS.
Logs and retrieves consumption data for bot operations.
"""
from typing import List
from datetime import date, datetime
from pydantic import BaseModel
from core.supabase import supabase_service_client


class BotLogResponse(BaseModel):
    """Response for bot log endpoints"""
    success: bool
    message: str
    data: dict = None


class BotLogListResponse(BaseModel):
    """Response for bot log list endpoints"""
    success: bool
    message: str
    data: List[dict] = None


class BotConsumptionLog(BaseModel):
    """Bot consumption log entry"""
    user_id: str
    food_name: str
    total_calories: float
    total_protein: float
    total_carbs: float
    total_fat: float


async def bot_log_consumption(log: BotConsumptionLog) -> BotLogResponse:
    """Log food consumption for a user (uses service role - no RLS)"""
    try:
        log_data = log.model_dump()
        response = supabase_service_client.schema("nutriguard").table("consumption_logs")\
            .insert(log_data)\
            .execute()
        
        if response.data:
            return BotLogResponse(
                success=True,
                message="Consumption logged successfully",
                data=response.data[0]
            )
        else:
            return BotLogResponse(
                success=False,
                message="Failed to log consumption"
            )
    except Exception as e:
        return BotLogResponse(
            success=False,
            message=f"Error logging consumption: {str(e)}"
        )


async def bot_get_user_logs(user_id: str, limit: int = 100) -> BotLogListResponse:
    """Get consumption logs for a user (uses service role - no RLS)"""
    try:
        response = supabase_service_client.schema("nutriguard").table("consumption_logs")\
            .select("*")\
            .eq("user_id", user_id)\
            .order("created_at", desc=True)\
            .limit(limit)\
            .execute()
        
        return BotLogListResponse(
            success=True,
            message="Logs retrieved successfully",
            data=response.data
        )
    except Exception as e:
        return BotLogListResponse(
            success=False,
            message=f"Error fetching logs: {str(e)}"
        )


async def bot_get_user_daily_totals(user_id: str, target_date: date) -> BotLogResponse:
    """Get daily nutrition totals for a user (uses service role - no RLS)"""
    try:
        response = supabase_service_client.schema("nutriguard").table("consumption_logs")\
            .select("total_calories, total_protein, total_carbs, total_fat")\
            .eq("user_id", user_id)\
            .gte("logged_at", str(target_date))\
            .lt("logged_at", str(date.fromordinal(target_date.toordinal() + 1)))\
            .execute()
        
        if response.data:
            # Sum all totals
            totals = {
                "date": str(target_date),
                "total_calories": sum(row["total_calories"] for row in response.data),
                "total_protein": sum(row["total_protein"] for row in response.data),
                "total_carbs": sum(row["total_carbs"] for row in response.data),
                "total_fat": sum(row["total_fat"] for row in response.data),
                "items_logged": len(response.data)
            }
            return BotLogResponse(
                success=True,
                message="Daily totals calculated",
                data=totals
            )
        else:
            return BotLogResponse(
                success=True,
                message="No logs for this date",
                data={
                    "date": str(target_date),
                    "total_calories": 0,
                    "total_protein": 0,
                    "total_carbs": 0,
                    "total_fat": 0,
                    "items_logged": 0
                }
            )
    except Exception as e:
        return BotLogResponse(
            success=False,
            message=f"Error calculating totals: {str(e)}"
        )


async def bot_get_today_logs(user_id: str) -> BotLogListResponse:
    """Get consumption logs for today for a user (uses service role - no RLS)"""
    try:
        today = date.today()
        tomorrow = date.fromordinal(today.toordinal() + 1)
        
        response = supabase_service_client.schema("nutriguard").table("consumption_logs")\
            .select("*")\
            .eq("user_id", user_id)\
            .gte("logged_at", str(today))\
            .lt("logged_at", str(tomorrow))\
            .order("logged_at", desc=True)\
            .execute()
        
        return BotLogListResponse(
            success=True,
            message="Today's logs retrieved successfully",
            data=response.data if response.data else []
        )
    except Exception as e:
        return BotLogListResponse(
            success=False,
            message=f"Error fetching today's logs: {str(e)}"
        )
