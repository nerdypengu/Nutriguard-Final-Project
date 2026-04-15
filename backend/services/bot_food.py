"""
Bot food service - uses service role key to bypass RLS.
Retrieves food data for bot operations without user restrictions.
"""
from typing import List, Optional
from pydantic import BaseModel
from core.supabase import supabase_service_client
from services.embeddings import generate_embedding


class BotFoodResponse(BaseModel):
    """Response for bot food endpoints"""
    success: bool
    message: str
    data: Optional[dict] = None


class BotFoodListResponse(BaseModel):
    """Response for bot food list endpoints"""
    success: bool
    message: str
    data: Optional[List[dict]] = None


async def get_bot_food(food_id: str) -> BotFoodResponse:
    """Get a specific food item (uses service role - no RLS)"""
    try:
        response = supabase_service_client.schema("nutriguard").table("food_items")\
            .select("id, name, calories, protein, fat, carbs, base_serving_size, is_user_contributed, created_by, created_at")\
            .eq("id", food_id)\
            .single()\
            .execute()
        
        if response.data:
            return BotFoodResponse(
                success=True,
                message="Food item retrieved successfully",
                data=response.data
            )
        else:
            return BotFoodResponse(
                success=False,
                message="Food item not found"
            )
    except Exception as e:
        return BotFoodResponse(
            success=False,
            message=f"Error fetching food item: {str(e)}"
        )


async def search_bot_food_by_name(name: str) -> BotFoodListResponse:
    """Search food by name (uses service role - no RLS)"""
    try:
        # Fetch ALL foods first to avoid the ilike filter that causes Supabase errors
        response = supabase_service_client.schema("nutriguard").table("food_items")\
            .select("id, name, calories, protein, fat, carbs, base_serving_size, is_user_contributed, created_by, created_at")\
            .execute()
        
        # Filter on client side
        search_name_lower = name.lower()
        filtered_data = [
            item for item in (response.data or [])
            if search_name_lower in item.get('name', '').lower()
        ]
        
        return BotFoodListResponse(
            success=True,
            message="Foods found",
            data=filtered_data
        )
    except Exception as e:
        return BotFoodListResponse(
            success=False,
            message=f"Error searching foods: {str(e)}"
        )


async def semantic_search_bot_food(query: str, limit: int = 10) -> BotFoodListResponse:
    """Semantic search food (uses service role - no RLS)"""
    try:
        # Always use text search for reliability - RPC has issues on Supabase
        result = await search_bot_food_by_name(query)
        
        # Apply the limit if we found results
        if result.success and result.data:
            result.data = result.data[:limit]
            
        return result
    except Exception as e:
        return BotFoodListResponse(
            success=False,
            message=f"Error in semantic search: {str(e)}"
        )
