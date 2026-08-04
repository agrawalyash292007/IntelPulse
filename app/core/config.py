from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # Application Configs
    PROJECT_NAME: str = "IntelPulse API"
    API_V1_STR: str = "/api/v1"
    ENVIRONMENT: str = "development"
    DATABASE_URL: str = "sqlite+aiosqlite:///./intelpulse.db"
    
    # Security Key
    SECRET_KEY: str

    # Automatically load values from the .env file in the root directory
    model_config = SettingsConfigDict(
        env_file=".env", 
        env_file_encoding="utf-8",
        extra="ignore"
    )

# Instantiate settings object to import across the application
settings = Settings()
