from pydantic import BaseModel
from typing import Optional, List
from datetime import date
from uuid import uuid4
from core.supabase import supabase_service_client

class ConsumptionLog(BaseModel):
    id: Optional[str] = None
    user_id: str
    food_name: str
    total_calories: Optional[float] = None
    total_protein: float
    total_carbs: float
    total_fat: float
    logged_at: Optional[str] = None
    created_at: Optional[str] = None

class LogResponse(BaseModel):
    success: bool
    message: str
    data: dict = None

class LogListResponse(BaseModel):
    success: bool
    message: str
    data: List[dict] = None

# Consumption Logs CRUD

async def log_consumption(log: ConsumptionLog) -> LogResponse:
    """Log food consumption for a user"""
    try:
        log_dict = log.model_dump(exclude={"id", "created_at"})
        log_dict["id"] = str(uuid4())  # Generate UUID on client side
        response = supabase_service_client.schema("nutriguard").table("consumption_logs").insert(log_dict).execute()
        
        if response.data:
            return LogResponse(
                success=True,
                message="Consumption logged successfully",
                data=response.data[0]
            )
        else:
            return LogResponse(
                success=False,
                message="Failed to log consumption"
            )
    except Exception as e:
        return LogResponse(
            success=False,
            message=f"Error logging consumption: {str(e)}"
        )

async def get_user_logs(user_id: str, limit: int = 100) -> LogListResponse:
    """Get all consumption logs for a user"""
    try:
        response = supabase_service_client.schema("nutriguard").table("consumption_logs").select("*").eq("user_id", user_id).order("logged_at", desc=True).limit(limit).execute()
        
        return LogListResponse(
            success=True,
            message="Consumption logs fetched successfully",
            data=response.data
        )
    except Exception as e:
        return LogListResponse(
            success=False,
            message=f"Error fetching logs: {str(e)}"
        )

async def get_user_logs_by_date(user_id: str, target_date: date) -> LogListResponse:
    """Get consumption logs for a specific date"""
    try:
        date_str = target_date.isoformat()
        response = supabase_service_client.schema("nutriguard").table("consumption_logs").select("*").eq("user_id", user_id).gte("logged_at", f"{date_str}T00:00:00").lt("logged_at", f"{date_str}T23:59:59").execute()
        
        return LogListResponse(
            success=True,
            message=f"Logs for {date_str} fetched successfully",
            data=response.data
        )
    except Exception as e:
        return LogListResponse(
            success=False,
            message=f"Error fetching logs: {str(e)}"
        )

async def get_daily_totals(user_id: str, target_date: date) -> LogResponse:
    """Get daily nutrition totals for a user"""
    try:
        date_str = target_date.isoformat()
        response = supabase_service_client.schema("nutriguard").table("consumption_logs").select("*").eq("user_id", user_id).gte("logged_at", f"{date_str}T00:00:00").lt("logged_at", f"{date_str}T23:59:59").execute()
        
        if response.data:
            totals = {
                "date": date_str,
                "total_calories": sum(log["total_calories"] for log in response.data),
                "total_protein": sum(log["total_protein"] for log in response.data),
                "total_carbs": sum(log["total_carbs"] for log in response.data),
                "total_fat": sum(log["total_fat"] for log in response.data),
                "items_logged": len(response.data)
            }
            return LogResponse(
                success=True,
                message="Daily totals calculated",
                data=totals
            )
        else:
            return LogResponse(
                success=True,
                message="No logs found for this date",
                data={
                    "date": date_str,
                    "total_calories": 0,
                    "total_protein": 0,
                    "total_carbs": 0,
                    "total_fat": 0,
                    "items_logged": 0
                }
            )
    except Exception as e:
        return LogResponse(
            success=False,
            message=f"Error calculating totals: {str(e)}"
        )

async def update_log(log_id: str, log: ConsumptionLog) -> LogResponse:
    """Update a consumption log"""
    try:
        log_dict = log.model_dump(exclude={"id", "created_at"})
        response = supabase_service_client.schema("nutriguard").table("consumption_logs").update(log_dict).eq("id", log_id).execute()
        
        if response.data:
            return LogResponse(
                success=True,
                message="Log updated successfully",
                data=response.data[0]
            )
        else:
            return LogResponse(
                success=False,
                message="Log not found"
            )
    except Exception as e:
        return LogResponse(
            success=False,
            message=f"Error updating log: {str(e)}"
        )

async def delete_log(log_id: str) -> LogResponse:
    """Delete a consumption log"""
    try:
        response = supabase_service_client.schema("nutriguard").table("consumption_logs").delete().eq("id", log_id).execute()
        return LogResponse(
            success=True,
            message="Log deleted successfully"
        )
    except Exception as e:
        return LogResponse(
            success=False,
            message=f"Error deleting log: {str(e)}"
        )
