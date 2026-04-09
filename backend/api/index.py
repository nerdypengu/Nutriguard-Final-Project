import sys
import os
from pathlib import Path

# Add the backend directory to the path so imports work correctly
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

# Load environment variables before importing main
from dotenv import load_dotenv
load_dotenv()

import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Redis connection status early
logger.info("Initializing Redis...")
try:
    from core.redis import get_redis_client
    import asyncio
    
    async def test_redis():
        client = await get_redis_client()
        if client:
            logger.info("✓ Redis is available")
            return True
        else:
            logger.warning("⚠ Redis unavailable - using fallback cache")
            return False
    
    # Try to test Redis async
    try:
        asyncio.run(test_redis())
    except:
        logger.warning("⚠ Redis connection test failed - API will use in-memory fallback")
except Exception as e:
    logger.warning(f"⚠ Redis initialization error: {e}")

try:
    from main import app
except Exception as e:
    logger.error(f"Error importing main: {e}")
    import traceback
    traceback.print_exc()
    raise

# Add a simple health check endpoint before main routers
@app.get("/health")
async def health_check():
    """Simple health check endpoint"""
    return {
        "status": "ok",
        "service": "NutriGuard Backend API",
        "environment": "vercel" if os.getenv("VERCEL") else "local"
    }

# Vercel expects a callable named 'app' for ASGI applications
__all__ = ['app']
