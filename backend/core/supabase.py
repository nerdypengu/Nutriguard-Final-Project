import os
from supabase import create_client, Client
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get Supabase credentials from environment variables
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

def get_supabase_client() -> Client:
    """
    Initialize and return a Supabase client instance (with RLS).
    
    Uses the anon key - respects RLS policies.
    Use for normal user operations.
    
    Make sure to set SUPABASE_URL and SUPABASE_KEY in your .env file:
    SUPABASE_URL=https://your-project.supabase.co
    SUPABASE_KEY=your-anon-key
    """
    if not SUPABASE_URL or not SUPABASE_KEY:
        raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set in environment variables")
    
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
    return supabase


def get_supabase_service_client() -> Client:
    """
    Initialize and return a Supabase service role client (bypasses RLS).
    
    Uses the service role key - BYPASSES RLS policies.
    Use for bot operations only - backend has full database access.
    
    Make sure to set SUPABASE_SERVICE_ROLE_KEY in your .env file:
    SUPABASE_SERVICE_ROLE_KEY=your-service-role-key
    """
    if not SUPABASE_URL or not SUPABASE_SERVICE_ROLE_KEY:
        raise ValueError("SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY must be set in environment variables")
    
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)
    return supabase

# Create global client instances
supabase_client = get_supabase_client()  # Normal user operations (with RLS)
supabase_service_client = get_supabase_service_client()  # Bot operations (no RLS)
