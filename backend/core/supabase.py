import os
from supabase import create_client, Client
from dotenv import load_dotenv
import logging

logger = logging.getLogger(__name__)

# Load environment variables from .env file
load_dotenv()

# Get Supabase credentials from environment variables
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

# Global client cache (lazy initialization)
_supabase_client: Client = None
_supabase_service_client: Client = None


def get_supabase_client() -> Client:
    """
    Get or create Supabase client instance (with RLS).
    
    ✨ LAZY INITIALIZATION: Only creates client when first called, not at import time.
    
    Uses the anon key - respects RLS policies.
    Use for normal user operations.
    
    Raises:
        ValueError: If SUPABASE_URL or SUPABASE_KEY are not set
    """
    global _supabase_client
    
    if _supabase_client is None:
        if not SUPABASE_URL or not SUPABASE_KEY:
            raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set in environment variables")
        
        try:
            _supabase_client = create_client(SUPABASE_URL, SUPABASE_KEY)
            logger.info("✓ Supabase client (RLS) initialized")
        except Exception as e:
            logger.error(f"✗ Failed to initialize Supabase client: {e}")
            raise
    
    return _supabase_client


def get_supabase_service_client() -> Client:
    """
    Get or create Supabase service role client (bypasses RLS).
    
    ✨ LAZY INITIALIZATION: Only creates client when first called, not at import time.
    
    Uses the service role key - BYPASSES RLS policies.
    Use for bot operations only - backend has full database access.
    
    Raises:
        ValueError: If SUPABASE_URL or SUPABASE_SERVICE_ROLE_KEY are not set
    """
    global _supabase_service_client
    
    if _supabase_service_client is None:
        if not SUPABASE_URL or not SUPABASE_SERVICE_ROLE_KEY:
            error_msg = "SUPABASE_SERVICE_ROLE_KEY not set - service client unavailable"
            logger.warning(f"⚠ {error_msg}")
            raise ValueError(f"SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY must be set in environment variables. {error_msg}")
        
        try:
            _supabase_service_client = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)
            logger.info("✓ Supabase client (Service Role) initialized")
        except Exception as e:
            logger.error(f"✗ Failed to initialize Supabase service client: {e}")
            raise
    
    return _supabase_service_client


# Wrapper classes for backward compatibility
# If services use: from core.supabase import supabase_client
# They now get a lazy-loading wrapper, not immediate initialization
class _LazySupabaseClient:
    """Wrapper that delays Supabase client initialization until first use"""
    
    def __getattr__(self, name):
        # When ANY method/attribute is accessed, trigger initialization
        client = get_supabase_client()
        return getattr(client, name)


class _LazySupabaseServiceClient:
    """Wrapper that delays Supabase service client initialization until first use"""
    
    def __getattr__(self, name):
        # When ANY method/attribute is accessed, trigger initialization
        client = get_supabase_service_client()
        return getattr(client, name)


# These are now lazy wrappers, not eager clients
# Initialization happens only when first accessed
supabase_client = _LazySupabaseClient()
supabase_service_client = _LazySupabaseServiceClient()
