"""
Application Configuration Settings
"""
from pydantic_settings import BaseSettings
from typing import Optional
import os

class Settings(BaseSettings):
    """Application settings with environment variable support"""
    
    # Application settings
    app_name: str = "TTKi AI Terminal"
    version: str = "2.0.0"
    debug: bool = False
    
    # Server settings
    host: str = "0.0.0.0"
    port: int = 8000
    
    # Legacy support
    enable_legacy_support: bool = True
    legacy_port: int = 5001
    
    # Database settings
    database_url: Optional[str] = None
    database_type: str = "memory"  # memory, postgresql, sqlite
    
    # AI/ML settings
    gemini_api_key: Optional[str] = None
    max_agent_instances: int = 10
    task_timeout: int = 300  # seconds
    
    # Logging
    log_level: str = "INFO"
    log_format: str = "structured"
    
    # Security
    cors_origins: list = ["*"]
    api_rate_limit: int = 100  # requests per minute
    
    # Performance
    max_concurrent_tasks: int = 5
    agent_pool_size: int = 20
    
    class Config:
        env_file = ".env"
        env_prefix = "TTKI_"
        case_sensitive = False
        extra = "ignore"  # Ignore extra environment variables

# Global settings instance
_settings: Optional[Settings] = None

def get_settings() -> Settings:
    """Get application settings (singleton)"""
    global _settings
    
    if _settings is None:
        _settings = Settings()
    
    return _settings

def reload_settings():
    """Reload settings from environment"""
    global _settings
    _settings = None
    return get_settings()
