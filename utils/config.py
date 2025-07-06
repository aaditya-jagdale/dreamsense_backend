import os
from typing import Optional
from pydantic_settings import BaseSettings
from pydantic import Field

class Settings(BaseSettings):
    """Application settings with environment variable support"""
    
    # Supabase settings
    supabase_url: str = Field(..., env="SUPABASE_URL")
    supabase_key: str = Field(..., env="SUPABASE_KEY")
    
    # Google Cloud settings
    google_service_account_json_b64: str = Field(..., env="GOOGLE_SERVICE_ACCOUNT_JSON_B64")
    
    # API Keys
    gemini_api_key: str = Field(..., env="GEMINI_API_KEY")
    elevenlabs_api_key: str = Field(..., env="ELEVENLABS_API_KEY")
    
    # App settings
    app_name: str = Field(default="DreamSense API", env="APP_NAME")
    app_version: str = Field(default="1.0.0", env="APP_VERSION")
    debug: bool = Field(default=False, env="DEBUG")
    
    # Subscription settings
    package_name: str = Field(default="com.dreamsenseuser.app", env="PACKAGE_NAME")
    subscription_id: str = Field(default="dreamsense_pro_1", env="SUBSCRIPTION_ID")
    
    # Free trial settings
    free_trial_dreams: int = Field(default=2, env="FREE_TRIAL_DREAMS")
    
    class Config:
        env_file = ".env"
        case_sensitive = False
        extra = "ignore"  # Allow extra environment variables

# Global settings instance
settings = Settings()

def get_setting(key: str, default: Optional[str] = None) -> str:
    """Get setting value with fallback to environment variable"""
    if hasattr(settings, key):
        return getattr(settings, key)
    return os.getenv(key, default) if default else os.getenv(key) 