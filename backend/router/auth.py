from fastapi import APIRouter, HTTPException, status, Request
from core.rate_limit import limiter, RATE_LIMITS
from services.auth import (
    sign_up,
    sign_in,
    sign_out,
    SignUpRequest,
    SignInRequest,
    AuthResponse,
    KeycloakAuthRequest,
    keycloak_authenticate
)
from services.bot_auth import authenticate_bot, BotAuthRequest, BotTokenResponse

router = APIRouter(
    prefix="/api/auth",
    tags=["auth"],
    responses={404: {"description": "Not found"}},
)

@router.post("/signup", response_model=AuthResponse)
@limiter.limit(RATE_LIMITS["auth"])
async def signup_endpoint(request: Request, signup_data: SignUpRequest):
    """
    Register a new user with email and password.
    Returns JWT access token for immediate use.
    Rate limited: 5 requests per minute
    """
    return await sign_up(signup_data.email, signup_data.password)

@router.post("/signin", response_model=AuthResponse)
@limiter.limit(RATE_LIMITS["auth"])
async def signin_endpoint(request: Request, signin_data: SignInRequest):
    """
    Login user with email and password.
    Returns JWT access token required for protected endpoints.
    Rate limited: 5 requests per minute
    """
    return await sign_in(signin_data.email, signin_data.password)

@router.post("/signout", response_model=AuthResponse)
async def signout_endpoint():
    """Logout user (frontend should discard JWT token)"""
    return await sign_out()

@router.post("/keycloak", response_model=AuthResponse)
@limiter.limit(RATE_LIMITS["auth"])
async def keycloak_endpoint(request: Request, auth_data: KeycloakAuthRequest):
    """
    Login or sign up user via Keycloak authorization code.
    Returns JWT access token required for protected endpoints.
    Rate limited: 5 requests per minute
    """
    return await keycloak_authenticate(auth_data.code, auth_data.redirect_uri)


@router.post("/bot/authenticate", response_model=BotTokenResponse)
@limiter.limit(RATE_LIMITS["auth"])
async def bot_authenticate_endpoint(request: Request, auth_request: BotAuthRequest):
    """
    Authenticate a bot/service account and get JWT token.
    Token lasts for 24 hours.
    
    Used by: n8n workflows, Discord bot integrations
    
    Example:
        POST /api/auth/bot/authenticate
        {
            "api_key": "your-bot-api-key"
        }
    
    Returns:
        {
            "access_token": "jwt-token-here",
            "token_type": "bearer",
            "expires_in": 86400,
            "issued_at": "2026-04-05T12:30:45.123456Z",
            "expires_at": "2026-04-06T12:30:45.123456Z"
        }
    
    You can use the timestamps to check if token is still valid:
        current_time = datetime.utcnow()
        expires_at = datetime.fromisoformat(response['expires_at'].replace('Z', '+00:00'))
        is_valid = current_time < expires_at
    
    Rate limited: 5 requests per minute
    """
    return await authenticate_bot(auth_request.api_key)
