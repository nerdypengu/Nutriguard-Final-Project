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

# Log that we're starting (without running async code at import time)
logger.info("NutriGuard Backend initializing...")

try:
    from main import app
except Exception as e:
    logger.error(f"✗ Fatal error importing main: {e}")
    import traceback
    traceback.print_exc()
    raise

# Add a simple health check endpoint
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
