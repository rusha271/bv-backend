from pydantic_settings import BaseSettings
from typing import List, Optional, Union
from pydantic import validator, field_validator
import os

class Settings(BaseSettings):
    DATABASE_URL: str = "mysql+pymysql://root:root@localhost/brahmavastu"
    JWT_SECRET_KEY: str = "....."
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    FRONTEND_ORIGINS: Union[List[str], str] = []
    FRONTEND_URL: Optional[str] = None
    ENV: str = "production"
    ENCRYPTION_KEY: str = "4cV9kH6sD2nP1yQ7wT5lJ3xA8oF2zE9rB1vL6mK7pN0="
    secret_key: str = "b9d4e7f0a1c2b3d5e6f7a8c9b0d1e2f3a4c5b6d7e8f9a0c1d2e3f4b5c6d7e8f"
    
    class Config:
        # Disable automatic JSON parsing for list fields
        env_parse_none_str = True

    @field_validator("ENV", mode="before")
    @classmethod
    def normalize_env(cls, v):
        """Normalize environment variable from ENVIRONMENT or ENV"""
        if v is None:
            # Try to get from ENVIRONMENT variable if ENV is not set
            return os.getenv("ENVIRONMENT", "production").lower()
        return str(v).lower()

    def get_frontend_origins(self) -> List[str]:
        """Get frontend origins based on environment and configuration"""
        # Handle different input types
        if not self.FRONTEND_ORIGINS:
            origins = []
        elif isinstance(self.FRONTEND_ORIGINS, str):
            # Parse comma-separated string
            origins = [origin.strip() for origin in self.FRONTEND_ORIGINS.split(",") if origin.strip()]
        elif isinstance(self.FRONTEND_ORIGINS, list):
            origins = [origin.strip() for origin in self.FRONTEND_ORIGINS if origin.strip()]
        else:
            origins = []
        
        # Environment-specific defaults
        if self.ENV.lower() == "production":
            default_origins = [
                "https://bharmaspace.com",
                "https://www.bharmaspace.com",
                "https://api.bharmaspace.com"
            ]
        else:
            default_origins = [
                "http://localhost:3000",
                "http://localhost:3001",
                "http://localhost:3002"
            ]
        
        # Use provided origins or fall back to defaults
        if origins:
            return origins
        else:
            return default_origins


settings = Settings()
