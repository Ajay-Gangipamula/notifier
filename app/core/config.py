from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "postgresql://notification_user:notification_pass@localhost:5432/notification_db"
    
    # Celery
    CELERY_BROKER_URL: str = "pyamqp://notification_user:notification_pass@localhost:5672//"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/0"
    
    # API
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Notification Orchestrator"
    SECRET_KEY: str = "your-super-secret-key-change-in-production"
    
    # Notification Settings
    MAX_RETRY_ATTEMPTS: int = 3
    RETRY_BACKOFF_FACTOR: float = 2.0
    BATCH_SIZE: int = 100
    
    # Email Settings
    SMTP_HOST: Optional[str] = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    
    # SMS Settings
    TWILIO_ACCOUNT_SID: Optional[str] = None
    TWILIO_AUTH_TOKEN: Optional[str] = None
    TWILIO_PHONE_NUMBER: Optional[str] = None
    
    # Push Notification
    FCM_SERVER_KEY: Optional[str] = None
    
    # Development
    DEBUG: bool = True
    LOG_LEVEL: str = "INFO"
    
    class Config:
        env_file = ".env"

settings = Settings()