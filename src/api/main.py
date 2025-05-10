"""
Main FastAPI application for the FAS analysis system.
"""

import sys
from pathlib import Path

# Add project root to Python path
project_root = str(Path(__file__).parent.parent.parent)
if project_root not in sys.path:
    sys.path.append(project_root)

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.api.endpoints import router as api_router

app = FastAPI(
    title="FAS Analysis API",
    description="API for analyzing financial transactions against AAOIFI FAS standards",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(api_router, prefix="/api")

@app.get("/")
async def root():
    """Root endpoint returning API information."""
    return {
        "name": "FAS Analysis API",
        "version": "1.0.0",
        "description": "API for analyzing financial transactions against AAOIFI FAS standards",
        "endpoints": {
            "/api/analyze-transaction": "POST - Analyze a financial transaction"
        }
    } 