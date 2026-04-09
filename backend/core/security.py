"""
JWT and security utilities for NutriGuard Backend
"""
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer
from core.config import JWT_SECRET_KEY, JWT_ALGORITHM, ACCESS_TOKEN_EXPIRE_TIMEDELTA

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# HTTP Bearer scheme for FastAPI
security = HTTPBearer()

class TokenData:
    def __init__(self, user_id: str = None, email: str = None):
        self.user_id = user_id
        self.email = email

def create_access_token(user_id: str, email: str) -> str:
    """
    Create a JWT access token for a user.
    
    Args:
        user_id: UUID of the user
        email: Email of the user
    
    Returns:
        JWT token string
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
    Verify and decode a JWT access token.
    
    Args:
        token: JWT token string
    
    Returns:
        TokenData with user_id and email
    
    Raises:
        HTTPException if token is invalid
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

def verify_bot_token(token: str) -> dict:
    """
    Verify and decode a bot JWT token.
    
    Args:
        token: JWT token string
    
    Returns:
        Token payload with bot service info
    
    Raises:
        HTTPException if token is invalid
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
    Dependency to get current authenticated user from JWT token.
    
    Usage in endpoints:
        @router.get("/protected")
        async def protected_endpoint(current_user: TokenData = Depends(get_current_user)):
            return {"user_id": current_user.user_id}
    """
    token = credentials.credentials
    return verify_access_token(token)

def hash_password(password: str) -> str:
    """Hash a password using bcrypt. Passwords are truncated to 72 bytes (bcrypt limit)."""
    # Truncate to 72 bytes as per bcrypt limitation
    truncated_password = password[:72]
    return pwd_context.hash(truncated_password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash. Passwords are truncated to 72 bytes (bcrypt limit)."""
    # Truncate to 72 bytes as per bcrypt limitation
    truncated_password = plain_password[:72]
    return pwd_context.verify(truncated_password, hashed_password)
