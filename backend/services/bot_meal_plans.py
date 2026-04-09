"""
Bot meal plans service - uses service role key to bypass RLS.
Retrieves and manipulates any user's meal plans for bot operations.
"""
from typing import List, Optional
from datetime import date
from uuid import uuid4
from pydantic import BaseModel
from core.supabase import supabase_service_client


class BotMealPlan(BaseModel):
    """Input model for creating/updating meal plans"""
    user_id: str
    meal_name: str
    total_calories: float
    total_protein: float
    total_carbs: float
    total_fat: float
    planned_for_date: date
    status: Optional[str] = "Planned"


class BotMealPlanResponse(BaseModel):
    """Response for bot meal plan endpoints"""
    success: bool
    message: str
    data: Optional[dict] = None


class BotMealPlanListResponse(BaseModel):
    """Response for bot meal plan list endpoints"""
    success: bool
    message: str
    data: Optional[List[dict]] = None


async def get_bot_user_meal_plans(user_id: str) -> BotMealPlanListResponse:
    """Get all meal plans for a user (uses service role - no RLS)"""
    try:
        response = supabase_service_client.schema("nutriguard").table("meal_plans")\
            .select("*")\
            .eq("user_id", user_id)\
            .execute()
        
        return BotMealPlanListResponse(
            success=True,
            message="Meal plans retrieved successfully",
            data=response.data
        )
    except Exception as e:
        return BotMealPlanListResponse(
            success=False,
            message=f"Error fetching meal plans: {str(e)}"
        )


async def get_bot_user_current_meal_plan(user_id: str) -> BotMealPlanListResponse:
    """Get today's meal plans for a user (uses service role - no RLS)"""
    try:
        today = date.today()
        response = supabase_service_client.schema("nutriguard").table("meal_plans")\
            .select("*")\
            .eq("user_id", user_id)\
            .eq("planned_for_date", str(today))\
            .execute()
        
        return BotMealPlanListResponse(
            success=True,
            message="Current meal plans retrieved successfully",
            data=response.data
        )
    except Exception as e:
        return BotMealPlanListResponse(
            success=False,
            message=f"Error fetching current meal plans: {str(e)}"
        )


async def get_bot_user_meal_plans_by_date(user_id: str, target_date: date) -> BotMealPlanListResponse:
    """Get meal plans for a specific date (uses service role - no RLS)"""
    try:
        response = supabase_service_client.schema("nutriguard").table("meal_plans")\
            .select("*")\
            .eq("user_id", user_id)\
            .eq("planned_for_date", str(target_date))\
            .execute()
        
        return BotMealPlanListResponse(
            success=True,
            message="Meal plans retrieved successfully",
            data=response.data
        )
    except Exception as e:
        return BotMealPlanListResponse(
            success=False,
            message=f"Error fetching meal plans: {str(e)}"
        )


async def create_bot_meal_plan(plan: BotMealPlan) -> BotMealPlanResponse:
    """Create a meal plan for any user (uses service role - no RLS)"""
    try:
        plan_dict = plan.model_dump()
        plan_dict["id"] = str(uuid4())
        plan_dict["planned_for_date"] = plan.planned_for_date.isoformat()
        
        response = supabase_service_client.schema("nutriguard").table("meal_plans")\
            .insert(plan_dict)\
            .execute()
        
        if response.data:
            return BotMealPlanResponse(
                success=True,
                message="Meal plan created successfully",
                data=response.data[0]
            )
        else:
            return BotMealPlanResponse(
                success=False,
                message="Failed to create meal plan"
            )
    except Exception as e:
        return BotMealPlanResponse(
            success=False,
            message=f"Error creating meal plan: {str(e)}"
        )


async def update_bot_meal_plan(plan_id: str, plan_update: dict) -> BotMealPlanResponse:
    """Update a meal plan (uses service role - no RLS)"""
    try:
        # Don't allow updating these fields
        plan_update.pop("id", None)
        plan_update.pop("created_at", None)
        plan_update.pop("user_id", None)
        
        # Format date if present
        if "planned_for_date" in plan_update:
            if isinstance(plan_update["planned_for_date"], date):
                plan_update["planned_for_date"] = plan_update["planned_for_date"].isoformat()
        
        response = supabase_service_client.schema("nutriguard").table("meal_plans")\
            .update(plan_update)\
            .eq("id", plan_id)\
            .execute()
        
        if response.data:
            return BotMealPlanResponse(
                success=True,
                message="Meal plan updated successfully",
                data=response.data[0]
            )
        else:
            return BotMealPlanResponse(
                success=False,
                message="Failed to update meal plan"
            )
    except Exception as e:
        return BotMealPlanResponse(
            success=False,
            message=f"Error updating meal plan: {str(e)}"
        )
