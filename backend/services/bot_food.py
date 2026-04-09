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
        response = supabase_service_client.schema("nutriguard").table("food_items")\
            .select("id, name, calories, protein, fat, carbs, base_serving_size, is_user_contributed, created_by, created_at")\
            .ilike("name", f"%{name}%")\
            .not_.is_("embedding", "null")\
            .execute()
        
        return BotFoodListResponse(
            success=True,
            message="Foods found",
            data=response.data
        )
    except Exception as e:
        return BotFoodListResponse(
            success=False,
            message=f"Error searching foods: {str(e)}"
        )


async def semantic_search_bot_food(query: str, limit: int = 10) -> BotFoodListResponse:
    """Semantic search food (uses service role - no RLS)"""
    try:
        # Generate embedding for query
        embedding = generate_embedding(query)
        
        # Call RPC function - works with service role
        response = supabase_service_client.rpc(
            "search_foods",
            {
                "query_embedding": embedding,
                "similarity_threshold": 0.5,
                "max_results": limit
            }
        ).execute()
        
        return BotFoodListResponse(
            success=True,
            message="Semantic search completed",
            data=response.data
        )
    except Exception as e:
        return BotFoodListResponse(
            success=False,
            message=f"Error in semantic search: {str(e)}"
        )
