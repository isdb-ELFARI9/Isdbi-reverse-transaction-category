"""
Configuration management for the FAS analysis system.
"""

import os
from dotenv import load_dotenv
from pydantic_settings import BaseSettings

# Load environment variables
load_dotenv()

class Settings(BaseSettings):
    """Application settings."""
    # API Keys
    PINECONE_API_KEY: str = os.getenv("PINECONE_API_KEY", "")
    PINECONE_ENVIRONMENT: str = os.getenv("PINECONE_ENVIRONMENT", "")
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    
    # Pinecone Index Names
    PINECONE_INDEX_FAS: str = os.getenv("PINECONE_INDEX_FAS", "")
    PINECONE_INDEX_SS: str = os.getenv("PINECONE_INDEX_SS", "")

    PINECONE_INDEX_FAS_UPDATE: str = os.getenv("PINECONE_INDEX_FAS_UPDATE", "")
    PINECONE_INDEX_SS_UPDATE: str = os.getenv("PINECONE_INDEX_SS_UPDATE", "")

    


    
    # Vector Store Settings
    VECTOR_DIMENSION: int = 1536  # For text-embedding-3-small
    VECTOR_METRIC: str = "cosine"
    
    # LLM Settings
    MODEL_NAME: str = "gemini-2.0-flash"
    TEMPERATURE: float = 0.7
    
    # Additional Settings
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    LLM_PROVIDER: str = os.getenv("LLM_PROVIDER", "gemini")
    GEMINI_MODEL_NAME: str = os.getenv("GEMINI_MODEL_NAME", "gemini-pro")
    MAX_TOKENS: int = int(os.getenv("MAX_TOKENS", "1000"))
    AGENT_MAX_ITERATIONS: int = int(os.getenv("AGENT_MAX_ITERATIONS", "5"))
    VERBOSE: bool = os.getenv("VERBOSE", "True").lower() == "true"
    APP_HOST: str = os.getenv("APP_HOST", "0.0.0.0")
    
    class Config:
        env_file = ".env"
        extra = "allow"  # Allow extra fields in the settings

settings = Settings() 