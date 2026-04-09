from pydantic import BaseModel, EmailStr
from uuid import uuid4
from core.supabase import supabase_client, supabase_service_client
from core.security import create_access_token, hash_password, verify_password
from postgrest.exceptions import APIError

class SignUpRequest(BaseModel):
    email: str
    password: str

class SignInRequest(BaseModel):
    email: str
    password: str

class KeycloakAuthRequest(BaseModel):
    code: str
    redirect_uri: str

class AuthResponse(BaseModel):
    success: bool
    message: str
    user: dict = None
    access_token: str = None

async def sign_up(email: str, password: str) -> AuthResponse:
    """Create a new user account with hashed password"""
    try:
        # Check if user already exists (use service client to bypass RLS)
        response = supabase_service_client.schema("nutriguard").table("users").select("*").eq("email", email).execute()
        if response.data:
            return AuthResponse(
                success=False,
                message="User with this email already exists"
            )
        
        # Hash the password
        hashed_password = hash_password(password)
        
        # Create user record (use service client to bypass RLS for signup)
        user_data = {
            "id": str(uuid4()),  # Generate UUID on client side
            "email": email,
            "password_hash": hashed_password,
            "is_subscribed": False
        }
        response = supabase_service_client.schema("nutriguard").table("users").insert(user_data).execute()
        
        if response.data:
            user = response.data[0]
            return AuthResponse(
                success=True,
                message="User created successfully",
                user={
                    "id": user["id"],
                    "email": user["email"],
                    "discord_id": user.get("discord_id"),
                    "discord_username": user.get("discord_username"),
                    "is_subscribed": user.get("is_subscribed")
                }
            )
        else:
            return AuthResponse(
                success=False,
                message="Failed to create user"
            )
    except Exception as e:
        return AuthResponse(
            success=False,
            message=f"Sign up failed: {str(e)}"
        )

async def sign_in(email: str, password: str) -> AuthResponse:
    """Authenticate user and return JWT access token"""
    try:
        response = supabase_service_client.schema("nutriguard").table("users").select("*").eq("email", email).execute()
        
        if not response.data:
            return AuthResponse(
                success=False,
                message="Invalid email or password"
            )
        
        user = response.data[0]
        
        # Verify password
        if not verify_password(password, user.get("password_hash", "")):
            return AuthResponse(
                success=False,
                message="Invalid email or password"
            )
        
        # Generate JWT token
        access_token = create_access_token(user["id"], user["email"])
        
        return AuthResponse(
            success=True,
            message="Sign in successful",
            user={
                "id": user["id"],
                "email": user["email"],
                "discord_id": user.get("discord_id"),
                "discord_username": user.get("discord_username")
            },
            access_token=access_token
        )
    except Exception as e:
        return AuthResponse(
            success=False,
            message=f"Sign in failed: {str(e)}"
        )

async def sign_out() -> AuthResponse:
    """Sign out user (token invalidation handled by frontend)"""
    return AuthResponse(
        success=True,
        message="Sign out successful"
    )

async def get_current_user():
    """Get the current authenticated user"""
    try:
        user = supabase_client.auth.get_user()
        return user
    except Exception as e:
        return None

from keycloak import KeycloakOpenID
from core.config import KEYCLOAK_SERVER_URL, KEYCLOAK_REALM, KEYCLOAK_CLIENT_ID, KEYCLOAK_CLIENT_SECRET
import logging

def get_keycloak_client():
    return KeycloakOpenID(
        server_url=KEYCLOAK_SERVER_URL,
        client_id=KEYCLOAK_CLIENT_ID,
        realm_name=KEYCLOAK_REALM,
        client_secret_key=KEYCLOAK_CLIENT_SECRET
    )

async def keycloak_authenticate(code: str, redirect_uri: str) -> AuthResponse:
    """Exchange Keycloak authorization code, fetch user, handle signup/signin."""
    try:
        keycloak_openid = get_keycloak_client()
        
        # Exchange code for access token
        token_response = keycloak_openid.token(
            grant_type=['authorization_code'],
            code=code,
            redirect_uri=redirect_uri
        )
        
        # Get userinfo using the token
        userinfo = keycloak_openid.userinfo(token_response['access_token'])
        email = userinfo.get('email')
        
        if not email:
            return AuthResponse(
                success=False,
                message="Keycloak profile does not provide an email address."
            )
            
        # Check if user already exists
        response = supabase_service_client.schema("nutriguard").table("users").select("*").eq("email", email).execute()
        
        if not response.data:
            # User does NOT exist. Sign them up automatically
            user_data = {
                "id": str(uuid4()),
                "email": email,
                "password_hash": "", # No password login unless set later
                "is_subscribed": False
            }
            insert_resp = supabase_service_client.schema("nutriguard").table("users").insert(user_data).execute()
            if not insert_resp.data:
                return AuthResponse(
                    success=False,
                    message="Failed to auto-provision user from Keycloak profile."
                )
            user = insert_resp.data[0]
        else:
            # User exists. Sign them in.
            user = response.data[0]
            
        access_token = create_access_token(user["id"], user["email"])
        
        return AuthResponse(
            success=True,
            message="Keycloak sign-in successful",
            user={
                "id": user["id"],
                "email": user["email"],
                "discord_id": user.get("discord_id"),
                "discord_username": user.get("discord_username"),
                "is_subscribed": user.get("is_subscribed", False)
            },
            access_token=access_token
        )
        
    except Exception as e:
        logging.error(f"Keycloak auth failed: {e}")
        return AuthResponse(
            success=False,
            message=f"Keycloak authentication failed: {str(e)}"
        )
