from pydantic_settings import BaseSettings
from typing import List
import os


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # Application
    APP_NAME: str = "RepoDocAgent"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    
    # Database
    SUPABASE_URL: str = ""  # Optional - only needed for Supabase
    SUPABASE_KEY: str = ""  # Optional - only needed for Supabase
    DATABASE_URL: str = "sqlite:///./repo_doc_agent.db"  # Default to SQLite for local dev
    
    # LLM Providers
    GROQ_API_KEY: str = ""  # Required for AI features
    OPENAI_API_KEY: str = ""  # Optional fallback
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # Git Authentication
    GITHUB_TOKEN: str = ""
    GITLAB_TOKEN: str = ""
    
    # Webhook Security
    WEBHOOK_SECRET: str = "change-me-in-production"
    
    # Repository Constraints
    MAX_REPO_SIZE_MB: int = 50
    MAX_FILES: int = 500
    MAX_FILE_SIZE_MB: int = 1
    ANALYSIS_TIMEOUT_SECONDS: int = 300
    
    # Celery
    CELERY_BROKER_URL: str = "redis://localhost:6379/0"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/0"
    
    # CORS
    CORS_ORIGINS: str = "http://localhost:3000,http://localhost:5173"
    
    # Logging
    LOG_LEVEL: str = "INFO"
    
    # Temp storage for cloned repos
    TEMP_REPOS_DIR: str = "temp_repos"
    
    @property
    def cors_origins_list(self) -> List[str]:
        """Parse CORS origins into a list"""
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# Global settings instance
settings = Settings()

# Ensure temp repos directory exists
os.makedirs(settings.TEMP_REPOS_DIR, exist_ok=True)
