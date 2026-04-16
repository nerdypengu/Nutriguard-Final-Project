from pydantic import BaseModel, EmailStr
from typing import Optional
from uuid import uuid4
from core.supabase import supabase_client, supabase_service_client

class UserProfile(BaseModel):
    id: Optional[str] = None
    email: str
    discord_id: Optional[str] = None
    discord_username: Optional[str] = None
    is_subscribed: Optional[bool] = False
    created_at: Optional[str] = None

class UserPreferences(BaseModel):
    id: Optional[str] = None
    user_id: str
    diet_type: Optional[str] = "Standard"
    target_calories: int
    target_protein_g: int
    target_carbs_g: int
    target_fat_g: int
    preferred_generation_day: Optional[str] = "Sunday"
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

class UserPreferencesInput(BaseModel):
    """Input model for creating/updating user preferences (excludes auto-fields)"""
    diet_type: Optional[str] = "Standard"
    target_calories: int
    target_protein_g: int
    target_carbs_g: int
    target_fat_g: int
    preferred_generation_day: Optional[str] = "Sunday"

class UserResponse(BaseModel):
    success: bool
    message: str
    data: dict = None

class UserListResponse(BaseModel):
    success: bool
    message: str
    data: list = None

# User Profile CRUD

async def create_user(email: str, discord_id: str = None, discord_username: str = None) -> UserResponse:
    """Create a new user profile"""
    try:
        user_data = {
            "id": str(uuid4()),  # Generate UUID on client side
            "email": email,
            "discord_id": discord_id,
            "discord_username": discord_username,
            "is_subscribed": False
        }
        response = supabase_service_client.schema("nutriguard").table("users").insert(user_data).execute()
        
        if response.data:
            return UserResponse(
                success=True,
                message="User created successfully",
                data=response.data[0]
            )
        else:
            return UserResponse(
                success=False,
                message="Failed to create user"
            )
    except Exception as e:
        return UserResponse(
            success=False,
            message=f"Error creating user: {str(e)}"
        )

async def get_user_by_id(user_id: str) -> UserResponse:
    """Fetch a user by ID"""
    try:
        response = supabase_service_client.schema("nutriguard").table("users").select("*").eq("id", user_id).execute()
        
        if response.data:
            return UserResponse(
                success=True,
                message="User fetched successfully",
                data=response.data[0]
            )
        else:
            return UserResponse(
                success=False,
                message="User not found"
            )
    except Exception as e:
        return UserResponse(
            success=False,
            message=f"Error fetching user: {str(e)}"
        )

async def get_user_by_email(email: str) -> UserResponse:
    """Fetch a user by email"""
    try:
        response = supabase_service_client.schema("nutriguard").table("users").select("*").eq("email", email).execute()
        
        if response.data:
            return UserResponse(
                success=True,
                message="User fetched successfully",
                data=response.data[0]
            )
        else:
            return UserResponse(
                success=False,
                message="User not found"
            )
    except Exception as e:
        return UserResponse(
            success=False,
            message=f"Error fetching user: {str(e)}"
        )

async def get_all_users() -> UserListResponse:
    """Fetch all users"""
    try:
        response = supabase_service_client.schema("nutriguard").table("users").select("*").execute()
        return UserListResponse(
            success=True,
            message="Users fetched successfully",
            data=response.data
        )
    except Exception as e:
        return UserListResponse(
            success=False,
            message=f"Error fetching users: {str(e)}"
        )

async def update_user(user_id: str, discord_id: str = None, discord_username: str = None, is_subscribed: bool = None) -> UserResponse:
    """Update a user profile"""
    try:
        update_data = {}
        if discord_id is not None:
            update_data["discord_id"] = discord_id
        if discord_username is not None:
            update_data["discord_username"] = discord_username
        if is_subscribed is not None:
            update_data["is_subscribed"] = is_subscribed
        
        if not update_data:
            return UserResponse(
                success=False,
                message="No fields to update"
            )
        
        # Use service client for nutriguard schema access (bypasses RLS)
        response = supabase_service_client.schema("nutriguard").table("users").update(update_data).eq("id", user_id).execute()
        
        if response.data:
            return UserResponse(
                success=True,
                message="User updated successfully",
                data=response.data[0]
            )
        else:
            return UserResponse(
                success=False,
                message="User not found"
            )
    except Exception as e:
        return UserResponse(
            success=False,
            message=f"Error updating user: {str(e)}"
        )

async def delete_user(user_id: str) -> UserResponse:
    """Delete a user (cascades to related data)"""
    try:
        supabase_service_client.schema("nutriguard").table("users").delete().eq("id", user_id).execute()
        return UserResponse(
            success=True,
            message="User deleted successfully"
        )
    except Exception as e:
        return UserResponse(
            success=False,
            message=f"Error deleting user: {str(e)}"
        )

# User Preferences CRUD

async def create_user_preferences(preferences: UserPreferences) -> UserResponse:
    """Create user preferences"""
    try:
        pref_dict = preferences.model_dump(exclude={"id", "created_at", "updated_at"})
        pref_dict["id"] = str(uuid4())  # Generate UUID on client side
        response = supabase_service_client.schema("nutriguard").table("user_preferences").insert(pref_dict).execute()
        
        if response.data:
            return UserResponse(
                success=True,
                message="User preferences created successfully",
                data=response.data[0]
            )
        else:
            return UserResponse(
                success=False,
                message="Failed to create user preferences"
            )
    except Exception as e:
        return UserResponse(
            success=False,
            message=f"Error creating preferences: {str(e)}"
        )

async def get_user_preferences(user_id: str) -> UserResponse:
    """Get preferences for a user"""
    try:
        print(f"DEBUG: Fetching preferences for user {user_id}")
        response = supabase_service_client.schema("nutriguard").table("user_preferences").select("*").eq("user_id", user_id).execute()
        print(f"DEBUG: Response data: {response.data}")
        
        if response.data:
            return UserResponse(
                success=True,
                message="User preferences fetched successfully",
                data=response.data[0]
            )
        else:
            print(f"DEBUG: No preferences found for user {user_id}")
            return UserResponse(
                success=False,
                message="Preferences not found"
            )
    except Exception as e:
        print(f"DEBUG: Error fetching preferences - {type(e).__name__}: {str(e)}")
        import traceback
        traceback.print_exc()
        return UserResponse(
            success=False,
            message=f"Error fetching preferences: {str(e)}"
        )

async def update_user_preferences(user_id: str, preferences: UserPreferences) -> UserResponse:
    """Update user preferences"""
    try:
        print(f"DEBUG: Updating preferences for user {user_id}")
        pref_dict = preferences.model_dump(exclude={"id", "user_id", "created_at", "updated_at"})
        print(f"DEBUG: Update data: {pref_dict}")
        response = supabase_service_client.schema("nutriguard").table("user_preferences").update(pref_dict).eq("user_id", user_id).execute()
        print(f"DEBUG: Response data: {response.data}")
        
        if response.data:
            return UserResponse(
                success=True,
                message="User preferences updated successfully",
                data=response.data[0]
            )
        else:
            print(f"DEBUG: No preferences found to update for user {user_id}")
            return UserResponse(
                success=False,
                message="Preferences not found"
            )
    except Exception as e:
        print(f"DEBUG: Error updating preferences - {type(e).__name__}: {str(e)}")
        import traceback
        traceback.print_exc()
        return UserResponse(
            success=False,
            message=f"Error updating preferences: {str(e)}"
        )


async def delete_user_preferences(user_id: str) -> UserResponse:
    """Delete user preferences"""
    try:
        supabase_service_client.schema("nutriguard").table("user_preferences").delete().eq("user_id", user_id).execute()
        return UserResponse(
            success=True,
            message="User preferences deleted successfully"
        )
    except Exception as e:
        return UserResponse(
            success=False,
            message=f"Error deleting preferences: {str(e)}"
        )
