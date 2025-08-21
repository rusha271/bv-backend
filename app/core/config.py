from pydantic_settings import BaseSettings
from typing import List
from pydantic import validator

class Settings(BaseSettings):
    DATABASE_URL: str = "mysql+pymysql://root:root@localhost/brahmavastu"
    JWT_SECRET_KEY: str = "..."
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    FRONTEND_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:3001" , "http://localhost:3002"]
    ENV: str = "development"
    ENCRYPTION_KEY: str = "your-encryption-key-here"
    GOOGLE_CLIENT_ID: str = ""
    GOOGLE_CLIENT_SECRET: str = ""
    secret_key: str = ""

    @validator("FRONTEND_ORIGINS", pre=True)
    def assemble_origins(cls, v):
        if isinstance(v, str):
            return [i.strip().rstrip("/") for i in v.strip("[]").replace('"', '').split(",")]
        return v


settings = Settings()
