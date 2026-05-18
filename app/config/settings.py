from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")
    
    OPENAI_API_KEY: str
    OPENAI_BASE_URL: Optional[str] = "https://api.openai.com/v1"
    MODEL_NAME: str = "gpt-4o-mini"
    JWT_SECRET_KEY: str = "fallback_secret_change_me_in_production"
    JWT_ALGORITHM: str = "HS256"

settings = Settings()