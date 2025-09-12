# apps/api/middleware/cors.py
"""
CORS middleware configuration
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pii_scanner import get_config

def setup_cors(app: FastAPI):
    """Setup CORS middleware"""
    
    config = get_config()
    cors_config = config.get_section("api")
    
    if cors_config.get("cors_enabled", True):
        app.add_middleware(
            CORSMiddleware,
            allow_origins=cors_config.get("cors_origins", ["*"]),
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )