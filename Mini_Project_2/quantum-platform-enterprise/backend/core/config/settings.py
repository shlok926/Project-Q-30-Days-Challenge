from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    PROJECT_NAME: str = "Quantum Platform Enterprise"
    VERSION: str = "0.1.0"
    API_V1_STR: str = "/api/v1"
    
    SECRET_KEY: str = "change_me_in_production_extremely_secure_key_123"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    BACKEND_CORS_ORIGINS: List[str] = ["http://localhost:3000"]
    
    POSTGRES_SERVER: str = "postgresql+asyncpg://postgres:postgres@localhost/quantum_db"
    
    class Config:
        env_file = ".env"

settings = Settings()
