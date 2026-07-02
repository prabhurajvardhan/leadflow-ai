from pydantic_settings import BaseSettings
from typing import Optional
from functools import lru_cache


class Settings(BaseSettings):
    # Application
    APP_NAME: str = "LeadFlow AI"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    ENVIRONMENT: str = "development"
    
    # API
    API_V1_PREFIX: str = "/api/v1"
    
    # Security
    SECRET_KEY: str = "dev-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # Database
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/leadflow"
    DATABASE_POOL_SIZE: int = 20
    DATABASE_MAX_OVERFLOW: int = 10
    
    # Redis (for job queue)
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # Email Provider (Resend)
    EMAIL_PROVIDER: str = "resend"  # Options: smtp, resend
    RESEND_API_KEY: Optional[str] = None
    SMTP_HOST: str = "smtp.zoho.com"
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    SMTP_FROM_EMAIL: str = "hello@nanowareai.in"
    SMTP_FROM_NAME: str = "LeadFlow AI"
    SMTP_USE_TLS: bool = True
    
    # AI Providers
    OPENAI_API_KEY: Optional[str] = None
    ANTHROPIC_API_KEY: Optional[str] = None
    OPENROUTER_API_KEY: Optional[str] = None
    DEFAULT_AI_PROVIDER: str = "bedrock"  # Options: bedrock, openrouter, anthropic, openai
    
    # Amazon Bedrock
    AWS_ACCESS_KEY_ID: Optional[str] = None
    AWS_SECRET_ACCESS_KEY: Optional[str] = None
    AWS_REGION: str = "us-east-1"
    BEDROCK_MODEL_ID: str = "us.amazon.nova-micro-v1:0"
    
    # OpenRouter specific
    OPENROUTER_BASE_URL: str = "https://openrouter.ai/api/v1"
    OPENROUTER_DEFAULT_MODEL: str = "anthropic/claude-3-haiku"
    
    # Crawler
    CRAWLER_USER_AGENT: str = "LeadFlow AI Bot (+https://leadflow.ai/bot)"
    CRAWLER_REQUEST_TIMEOUT: int = 30
    CRAWLER_MAX_DEPTH: int = 3
    CRAWLER_CONCURRENT_REQUESTS: int = 5
    
    # Google Maps
    GOOGLE_MAPS_API_KEY: Optional[str] = None
    
    # Playwright
    PLAYWRIGHT_BROWSER: str = "chromium"
    PLAYWRIGHT_HEADLESS: bool = True
    
    # Email Settings
    EMAIL_DAILY_LIMIT: int = 100
    EMAIL_REPLY_TRACKING_ENABLED: bool = True
    EMAIL_REPLY_TRACKING_DOMAIN: Optional[str] = None
    
    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 60
    
    # CORS
    CORS_ORIGINS: list[str] = ["http://localhost:3000", "http://localhost:8000"]
    
    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
