from pydantic_settings import BaseSettings
from typing import List
from pydantic import validator

class Settings(BaseSettings):
    DATABASE_URL: str = "mysql+pymysql://root:root@localhost/brahmavastu"
    JWT_SECRET_KEY: str = "....."
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    FRONTEND_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:3001" , "http://localhost:3002"]
    ENV: str = "production"
    ENCRYPTION_KEY: str = "4cV9kH6sD2nP1yQ7wT5lJ3xA8oF2zE9rB1vL6mK7pN0="
    secret_key: str = "b9d4e7f0a1c2b3d5e6f7a8c9b0d1e2f3a4c5b6d7e8f9a0c1d2e3f4b5c6d7e8f"

    @validator("FRONTEND_ORIGINS", pre=True)
    def assemble_origins(cls, v):
        if isinstance(v, str):
            return [i.strip().rstrip("/") for i in v.strip("[]").replace('"', '').split(",")]
        return v


settings = Settings()
