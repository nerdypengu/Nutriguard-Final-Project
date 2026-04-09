"""
Entry point for ASGI application
Re-exports the FastAPI app from main.py for both local and production use
"""
from main import app

__all__ = ["app"]
