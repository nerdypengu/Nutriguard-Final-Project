from pydantic import BaseModel
from typing import List, Optional
from uuid import uuid4
from core.supabase import supabase_service_client
from services.embeddings import generate_embedding

import hashlib
import json

class FoodItem(BaseModel):
    id: Optional[str] = None
    name: str
    calories: float
    protein: float
    fat: float
    carbs: float
    base_serving_size: Optional[str] = "100g"
    is_user_contributed: Optional[bool] = False
    created_by: Optional[str] = None
    created_at: Optional[str] = None

class FoodResponse(BaseModel):
    success: bool
    message: str
    data: Optional[dict] = None

class FoodListResponse(BaseModel):
    success: bool
    message: str
    data: Optional[List[dict]] = None

def get_response_hash(data: list) -> str:
    """Generate a hash of the response data to detect changes"""
    json_str = json.dumps(data, sort_keys=True, default=str)
    return hashlib.md5(json_str.encode()).hexdigest()

# CRUD Operations for Food Items

async def create_food(food: FoodItem, created_by: str = None) -> FoodResponse:
    """Create a new food item with automatic embedding generation"""
    try:
        food_dict = food.model_dump(exclude={"id", "created_at"})
        food_dict["id"] = str(uuid4())  # Generate UUID on client side
        if created_by:
            food_dict["created_by"] = created_by
        
        # Generate embedding for the food name for semantic search
        embedding = generate_embedding(food.name)
        food_dict["embedding"] = embedding
        
        response = supabase_service_client.schema("nutriguard").table("food_items").insert(food_dict).execute()
        
        if response.data:
            return FoodResponse(
                success=True,
                message="Food item created successfully",
                data=response.data[0]
            )
        else:
            return FoodResponse(
                success=False,
                message="Failed to create food item"
            )
    except Exception as e:
        return FoodResponse(
            success=False,
            message=f"Error creating food item: {str(e)}"
        )

async def get_all_foods() -> FoodListResponse:
    """Fetch all food items"""
    try:
        # Use service role client to bypass RLS and see all data
        response = supabase_service_client.schema("nutriguard").table("food_items").select("id, name, calories, protein, fat, carbs, base_serving_size, is_user_contributed, created_by, created_at").execute()
        print(f"DEBUG: Response data: {response.data}")
        print(f"DEBUG: Response count: {len(response.data) if response.data else 0}")
        return FoodListResponse(
            success=True,
            message="Foods fetched successfully",
            data=response.data
        )
    except Exception as e:
        print(f"DEBUG: Error fetching foods - {str(e)}")
        return FoodListResponse(
            success=False,
            message=f"Error fetching foods: {str(e)}"
        )

async def get_food_by_id(food_id: str) -> FoodResponse:
    """Fetch a single food item by ID"""
    try:
        response = supabase_service_client.schema("nutriguard").table("food_items").select("*").eq("id", food_id).execute()
        
        if response.data:
            return FoodResponse(
                success=True,
                message="Food item fetched successfully",
                data=response.data[0]
            )
        else:
            return FoodResponse(
                success=False,
                message="Food item not found"
            )
    except Exception as e:
        return FoodResponse(
            success=False,
            message=f"Error fetching food item: {str(e)}"
        )

async def search_foods_by_name(name: str) -> FoodListResponse:
    """Search food items by name (fast text search) - filtering on client side to avoid Supabase serialization issues"""
    try:
        print(f"DEBUG: Searching for foods with name like '{name}'")
        # Fetch ALL foods first (avoids the ilike filter that's causing Supabase errors)
        response = supabase_service_client.schema("nutriguard").table("food_items").select("id, name, calories, protein, fat, carbs, base_serving_size, is_user_contributed, created_by, created_at").execute()
        
        # Filter on client side
        search_name_lower = name.lower()
        filtered_data = [
            item for item in (response.data or [])
            if search_name_lower in item.get('name', '').lower()
        ]
        
        print(f"DEBUG: Search response - found {len(filtered_data)} matches out of {len(response.data or [])} total items")
        return FoodListResponse(
            success=True,
            message=f"Foods matching '{name}' fetched successfully",
            data=filtered_data
        )
    except Exception as e:
        print(f"DEBUG: Search error - Type: {type(e).__name__}, Message: {str(e)}")
        import traceback
        traceback.print_exc()
        return FoodListResponse(
            success=False,
            message=f"Error searching foods: {str(e)}"
        )

async def semantic_search_foods(query: str, limit: int = 10) -> FoodListResponse:
    """
    Search for foods by name (fast text search with name matching).
    Falls back to text search for reliability.
    
    Example: searching "chicken" would match "grilled chicken breast"
    """
    try:
        # Always use text search for reliability - RPC has issues on Supabase
        # Text search is still very effective for food names
        return await search_foods_by_name(query)
    except Exception as e:
        print(f"DEBUG: Search failed: {str(e)}")
        return FoodListResponse(
            success=False,
            message=f"Error searching foods: {str(e)}"
        )



async def update_food(food_id: str, food: FoodItem) -> FoodResponse:
    """Update an existing food item"""
    try:
        food_dict = food.model_dump(exclude={"id", "created_at", "created_by"})
        
        # Regenerate embedding with updated food name
        embedding = generate_embedding(food.name)
        food_dict["embedding"] = embedding
        
        response = supabase_service_client.schema("nutriguard").table("food_items").update(food_dict).eq("id", food_id).execute()
        
        if response.data:
            return FoodResponse(
                success=True,
                message="Food item updated successfully",
                data=response.data[0]
            )
        else:
            return FoodResponse(
                success=False,
                message="Food item not found"
            )
    except Exception as e:
        return FoodResponse(
            success=False,
            message=f"Error updating food item: {str(e)}"
        )

async def delete_food(food_id: str) -> FoodResponse:
    """Delete a food item"""
    try:
        supabase_service_client.schema("nutriguard").table("food_items").delete().eq("id", food_id).execute()
        return FoodResponse(
            success=True,
            message="Food item deleted successfully"
        )
    except Exception as e:
        return FoodResponse(
            success=False,
            message=f"Error deleting food item: {str(e)}"
        )
