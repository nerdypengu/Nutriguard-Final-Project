"""
JWT and security utilities for NutriGuard Backend
"""
import uuid
import logging
import json
import base64
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer
from keycloak import KeycloakOpenID
from jwcrypto import jwk
from core.config import (
    JWT_SECRET_KEY, 
    JWT_ALGORITHM, 
    ACCESS_TOKEN_EXPIRE_TIMEDELTA,
    KEYCLOAK_SERVER_URL,
    KEYCLOAK_REALM,
    KEYCLOAK_CLIENT_ID,
    KEYCLOAK_CLIENT_SECRET
)
from core.supabase import supabase_service_client
from core.redis import get_cache, set_cache

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# HTTP Bearer scheme for FastAPI
security = HTTPBearer()

_keycloak_client = None
def get_keycloak_client():
    global _keycloak_client
    if _keycloak_client is None:
        _keycloak_client = KeycloakOpenID(
            server_url=KEYCLOAK_SERVER_URL,
            client_id=KEYCLOAK_CLIENT_ID,
            realm_name=KEYCLOAK_REALM,
            client_secret_key=KEYCLOAK_CLIENT_SECRET
        )
    return _keycloak_client

class TokenData:
    def __init__(self, user_id: str = None, email: str = None):
        self.user_id = user_id
        self.email = email

def create_access_token(user_id: str, email: str) -> str:
    """
    Create a JWT access token for a user.
    """
    to_encode = {
        "sub": user_id,
        "email": email,
        "iat": datetime.utcnow(),
        "exp": datetime.utcnow() + ACCESS_TOKEN_EXPIRE_TIMEDELTA
    }
    
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
    return encoded_jwt

def verify_access_token(token: str) -> TokenData:
    """
    Verify and decode a standard JWT access token.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        user_id: str = payload.get("sub")
        email: str = payload.get("email")
        
        if user_id is None or email is None:
            raise credentials_exception
        
        return TokenData(user_id=user_id, email=email)
    except JWTError:
        raise credentials_exception

async def verify_keycloak_token(token: str) -> TokenData:
    """
    Verify Keycloak token and perform JIT auto-provisioning.
    """
    kc = get_keycloak_client()
    try:
        # Fetch public key for token verification
        public_key = "-----BEGIN PUBLIC KEY-----\n" + kc.public_key() + "\n-----END PUBLIC KEY-----"
        
        # Use python-jose for standard reliable decoding instead of python-keycloak's internals
        payload = jwt.decode(
            token,
            key=public_key,
            algorithms=["RS256"],
            audience=KEYCLOAK_CLIENT_ID,
            options={"verify_aud": False, "verify_iss": False}
        )
        
        email = payload.get("email")
        logging.info(f"Token email: {email}")
        
        if not email:
            logging.error("Keycloak profile missing email claim")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Keycloak profile missing email",
                headers={"WWW-Authenticate": "Bearer"},
            )
            
        discord_username = payload.get("preferred_username")
        
        cache_key = f"auth:jit:{email}"
        cached_id = await get_cache(cache_key)
        
        if cached_id:
            logging.info(f"Found cached user ID for {email}")
            if isinstance(cached_id, bytes):
                cached_id = cached_id.decode('utf-8')
            return TokenData(user_id=cached_id, email=email)
        
        logging.info(f"JIT provisioning user: {email}")
        # JIT Provisioning (Check DB)
        resp = supabase_service_client.schema("nutriguard").table("users").select("id").eq("email", email).execute()
        if resp.data:
            user_id = resp.data[0]["id"]
            logging.info(f"Found existing user ID: {user_id}")
        else:
            user_id = str(uuid.uuid4())
            logging.info(f"Creating new user with ID: {user_id}")
            new_user = {
                "id": user_id,
                "email": email,
                "discord_username": discord_username if discord_username else None,
                "password_hash": "", # No password allowed
                "is_subscribed": False
            }
            insert_resp = supabase_service_client.schema("nutriguard").table("users").insert(new_user).execute()
            if not insert_resp.data:
                raise Exception("Failed to provision new user in Supabase")
            
        await set_cache(cache_key, user_id, 3600)  # 1 hour caching
        
        return TokenData(user_id=user_id, email=email)
        
    except Exception as e:
        logging.error(f"Keycloak verification error: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate Keycloak credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

def verify_bot_token(token: str) -> dict:
    """
    Verify and decode a bot JWT token.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid bot token",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        service: str = payload.get("service")
        
        if service != "bot":
            raise credentials_exception
        
        return payload
    except JWTError:
        raise credentials_exception

async def get_current_user(credentials = Depends(security)) -> TokenData:
    """
    Dependency to get current authenticated user from either Keycloak or Standard JWT token.
    """
    token = credentials.credentials
    
    try:
        # Decode without verification to inspect the issuer
        unverified_claims = jwt.get_unverified_claims(token)
        iss = unverified_claims.get("iss", "")
        
        logging.info(f"Token issuer: {iss}")
        
        # Check if this is a Keycloak token
        if "realms/nutriguard" in iss or "keycloak" in iss.lower() or "http" in iss.lower():
            logging.info("Detected Keycloak token, verifying with Keycloak...")
            return await verify_keycloak_token(token)
        else:
            logging.info("Detected standard JWT token, verifying locally...")
            return verify_access_token(token)
            
    except Exception as e:
        logging.error(f"Token verification failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

def hash_password(password: str) -> str:
    """Hash a password using bcrypt. Passwords are truncated to 72 bytes."""
    truncated_password = password[:72]
    return pwd_context.hash(truncated_password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash. Passwords are truncated to 72 bytes."""
    truncated_password = plain_password[:72]
    return pwd_context.verify(truncated_password, hashed_password)
