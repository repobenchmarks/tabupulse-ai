import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "TabuPulse AI"
    VERSION: str = "1.0.0"
    API_PREFIX: str = "/api"
    TABPFN_API_KEY: str = os.getenv("TABPFN_API_KEY", "")
    PORT: int = int(os.getenv("PORT", 8000))
    HOST: str = os.getenv("HOST", "0.0.0.0")

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()
