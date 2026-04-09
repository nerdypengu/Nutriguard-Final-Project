"""
Bot service account authentication.
Generates JWT tokens for bot/service accounts to access the API.
"""
from datetime import datetime, timedelta
from jose import jwt
from pydantic import BaseModel
from fastapi import HTTPException, status
from core.config import JWT_SECRET_KEY, JWT_ALGORITHM, BOT_API_KEY, BOT_SERVICE_ID


class BotAuthRequest(BaseModel):
    """Bot authentication request"""
    api_key: str


class BotTokenResponse(BaseModel):
    """Bot token response with timestamp information"""
    access_token: str
    token_type: str = "bearer"
    expires_in: int = 86400  # 24 hours in seconds
    issued_at: str  # ISO 8601 format when token was issued
    expires_at: str  # ISO 8601 format when token expires


async def authenticate_bot(api_key: str) -> BotTokenResponse:
    """
    Authenticate a bot/service account and return JWT token with timestamps.
    Token lasts for 24 hours.
    
    Args:
        api_key: The bot API key
        
    Returns:
        BotTokenResponse with access token and timestamp information
        
    Raises:
        HTTPException if API key is invalid
    """
    # Validate API key
    if api_key != BOT_API_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    # Calculate timestamps
    issued_at = datetime.utcnow()
    expires_at = issued_at + timedelta(hours=24)
    
    # Create JWT token for bot service account (24 hour expiration)
    to_encode = {
        "sub": BOT_SERVICE_ID,
        "service": "bot",
        "iat": issued_at,
        "exp": expires_at
    }
    
    access_token = jwt.encode(to_encode, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
    
    return BotTokenResponse(
        access_token=access_token,
        expires_in=86400,
        issued_at=issued_at.isoformat() + "Z",  # ISO 8601 format with Z for UTC
        expires_at=expires_at.isoformat() + "Z"
    )
