"""
Bot meal plans service - uses service role key to bypass RLS.
Retrieves and manipulates any user's meal plans for bot operations.
"""
from typing import List, Optional
from datetime import date
from uuid import uuid4
from pydantic import BaseModel, ConfigDict
from core.supabase import supabase_service_client
from enum import Enum

class BotMealType(str, Enum):
    BREAKFAST = "BREAKFAST"
    LUNCH = "LUNCH"
    DINNER = "DINNER"
    ADDITIONAL = "ADDITIONAL"

class BotMealPlan(BaseModel):
    """Input model for creating/updating meal plans"""
    user_id: str
    meal_type: BotMealType
    meal_name: str
    total_calories: float
    total_protein: float
    total_carbs: float
    total_fat: float
    planned_for_date: date
    status: Optional[str] = "Planned"
    
    model_config = ConfigDict(use_enum_values=True)


class BotMealPlanUpdate(BaseModel):
    """Input model for updating meal plans"""
    meal_type: Optional[BotMealType] = None
    meal_name: Optional[str] = None
    total_calories: Optional[float] = None
    total_protein: Optional[float] = None
    total_carbs: Optional[float] = None
    total_fat: Optional[float] = None
    planned_for_date: Optional[date] = None
    status: Optional[str] = None

    model_config = ConfigDict(use_enum_values=True)

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


async def update_bot_meal_plan(plan_id: str, plan_update: BotMealPlanUpdate) -> BotMealPlanResponse:
    """Update a meal plan (uses service role - no RLS)"""
    try:
        update_dict = plan_update.model_dump(exclude_unset=True)
        
        if not update_dict:
            return BotMealPlanResponse(
                success=False,
                message="No fields to update provided"
            )
            
        # Format date if present
        if "planned_for_date" in update_dict:
            if isinstance(update_dict["planned_for_date"], date):
                update_dict["planned_for_date"] = update_dict["planned_for_date"].isoformat()
        
        response = supabase_service_client.schema("nutriguard").table("meal_plans")\
            .update(update_dict)\
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
