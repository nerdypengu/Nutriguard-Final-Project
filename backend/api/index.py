import sys
import os
import traceback
from pathlib import Path

# Add the backend directory to the path so imports work correctly
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

# Load environment variables before importing main
from dotenv import load_dotenv  # noqa: E402
load_dotenv()

import logging  # noqa: E402
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Log startup info
logger.info("="*60)
logger.info("NutriGuard Backend initializing...")
logger.info(f"Environment: {os.getenv('ENVIRONMENT', 'unknown')}")
logger.info(f"SUPABASE_URL set: {bool(os.getenv('SUPABASE_URL'))}")
logger.info(f"SUPABASE_KEY set: {bool(os.getenv('SUPABASE_KEY'))}")
logger.info(f"SUPABASE_SERVICE_ROLE_KEY set: {bool(os.getenv('SUPABASE_SERVICE_ROLE_KEY'))}")
logger.info(f"JWT_SECRET_KEY set: {bool(os.getenv('JWT_SECRET_KEY'))}")
logger.info("="*60)

app = None
startup_error = None

try:
    from main import app
    logger.info("✓ Main app imported successfully")
except Exception as e:
    startup_error = {
        "error": str(e),
        "type": type(e).__name__,
        "traceback": traceback.format_exc()
    }
    logger.error(f"✗ Fatal error importing main: {e}")
    logger.error(f"Traceback:\n{startup_error['traceback']}")
    
    # Create minimal error app
    from fastapi import FastAPI
    from fastapi.responses import JSONResponse
    
    app = FastAPI()
    
    @app.get("/")
    async def root():
        return JSONResponse(
            status_code=500,
            content={
                "status": "error",
                "message": "Application failed to initialize",
                "error": startup_error["error"],
                "type": startup_error["type"],
                "note": "Check Vercel function logs for full traceback"
            }
        )
    
    @app.get("/health")
    async def health():
        return JSONResponse(
            status_code=500,
            content={"status": "error", "message": startup_error["error"]}
        )

# Vercel expects a callable named 'app' for ASGI applications
__all__ = ['app']
