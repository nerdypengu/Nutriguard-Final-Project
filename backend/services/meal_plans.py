from pydantic import BaseModel
from typing import Optional, List
from datetime import date
from uuid import uuid4
from core.supabase import supabase_service_client

class MealPlan(BaseModel):
    id: Optional[str] = None
    user_id: str
    meal_name: str
    total_calories: float
    total_protein: float
    total_carbs: float
    total_fat: float
    planned_for_date: date
    status: Optional[str] = "Planned"
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

class PlanResponse(BaseModel):
    success: bool
    message: str
    data: dict = None

class PlanListResponse(BaseModel):
    success: bool
    message: str
    data: List[dict] = None

# Meal Plans CRUD

async def create_meal_plan(plan: MealPlan) -> PlanResponse:
    """Create a new meal plan"""
    try:
        plan_dict = plan.model_dump(exclude={"id", "created_at", "updated_at"})
        plan_dict["id"] = str(uuid4())  # Generate UUID on client side
        plan_dict["planned_for_date"] = plan.planned_for_date.isoformat()
        response = supabase_service_client.schema("nutriguard").table("meal_plans").insert(plan_dict).execute()
        
        if response.data:
            return PlanResponse(
                success=True,
                message="Meal plan created successfully",
                data=response.data[0]
            )
        else:
            return PlanResponse(
                success=False,
                message="Failed to create meal plan"
            )
    except Exception as e:
        return PlanResponse(
            success=False,
            message=f"Error creating meal plan: {str(e)}"
        )

async def get_meal_plan(plan_id: str) -> PlanResponse:
    """Fetch a meal plan by ID"""
    try:
        response = supabase_service_client.schema("nutriguard").table("meal_plans").select("*").eq("id", plan_id).execute()
        
        if response.data:
            return PlanResponse(
                success=True,
                message="Meal plan fetched successfully",
                data=response.data[0]
            )
        else:
            return PlanResponse(
                success=False,
                message="Meal plan not found"
            )
    except Exception as e:
        return PlanResponse(
            success=False,
            message=f"Error fetching meal plan: {str(e)}"
        )

async def get_user_meal_plans(user_id: str) -> PlanListResponse:
    """Fetch all meal plans for a user"""
    try:
        response = supabase_service_client.schema("nutriguard").table("meal_plans").select("*").eq("user_id", user_id).order("planned_for_date", desc=True).execute()
        
        return PlanListResponse(
            success=True,
            message="Meal plans fetched successfully",
            data=response.data
        )
    except Exception as e:
        return PlanListResponse(
            success=False,
            message=f"Error fetching meal plans: {str(e)}"
        )

async def get_meal_plans_by_date(user_id: str, target_date: date) -> PlanListResponse:
    """Fetch meal plans for a specific date"""
    try:
        date_str = target_date.isoformat()
        response = supabase_service_client.schema("nutriguard").table("meal_plans").select("*").eq("user_id", user_id).eq("planned_for_date", date_str).execute()
        
        return PlanListResponse(
            success=True,
            message=f"Meal plans for {date_str} fetched successfully",
            data=response.data
        )
    except Exception as e:
        return PlanListResponse(
            success=False,
            message=f"Error fetching meal plans: {str(e)}"
        )

async def update_meal_plan(plan_id: str, plan: MealPlan) -> PlanResponse:
    """Update a meal plan"""
    try:
        plan_dict = plan.model_dump(exclude={"id", "created_at", "updated_at"})
        plan_dict["planned_for_date"] = plan.planned_for_date.isoformat()
        response = supabase_service_client.schema("nutriguard").table("meal_plans").update(plan_dict).eq("id", plan_id).execute()
        
        if response.data:
            return PlanResponse(
                success=True,
                message="Meal plan updated successfully",
                data=response.data[0]
            )
        else:
            return PlanResponse(
                success=False,
                message="Meal plan not found"
            )
    except Exception as e:
        return PlanResponse(
            success=False,
            message=f"Error updating meal plan: {str(e)}"
        )

async def update_meal_plan_status(plan_id: str, status: str) -> PlanResponse:
    """Update the status of a meal plan (e.g., Planned, In Progress, Completed)"""
    try:
        response = supabase_service_client.schema("nutriguard").table("meal_plans").update({"status": status}).eq("id", plan_id).execute()
        
        if response.data:
            return PlanResponse(
                success=True,
                message="Meal plan status updated successfully",
                data=response.data[0]
            )
        else:
            return PlanResponse(
                success=False,
                message="Meal plan not found"
            )
    except Exception as e:
        return PlanResponse(
            success=False,
            message=f"Error updating status: {str(e)}"
        )

async def delete_meal_plan(plan_id: str) -> PlanResponse:
    """Delete a meal plan"""
    try:
        response = supabase_service_client.schema("nutriguard").table("meal_plans").delete().eq("id", plan_id).execute()
        return PlanResponse(
            success=True,
            message="Meal plan deleted successfully"
        )
    except Exception as e:
        return PlanResponse(
            success=False,
            message=f"Error deleting meal plan: {str(e)}"
        )
