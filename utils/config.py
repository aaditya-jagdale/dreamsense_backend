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
    unrealspeech_api_key: str = Field(..., env="UNREALSPEECH_API_KEY")
    
    # App settings
    app_name: str = Field(default="DreamSense API", env="APP_NAME")
    app_version: str = Field(default="1.0.0", env="APP_VERSION")
    debug: bool = Field(default=False, env="DEBUG")
    
    # Subscription settings
    package_name: str = Field(default="com.dreamsense.app", env="PACKAGE_NAME")
    subscription_id: str = Field(default="dreamsense_pro_1", env="SUBSCRIPTION_ID")
    
    # Free trial settings
    free_trial_dreams: int = Field(default=5, env="FREE_TRIAL_DREAMS")
    
    # Test user settings
    test_user_ids: list[str] = Field(default=["9e90cd1a-f665-47fb-9903-1b03285e9f6d","7b9428dd-5bcf-41b3-95ec-bd00819ca3d6","c8b285f4-e34a-4468-b1fa-19d2244dc164"])
    
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

def is_test_user(user_id: str) -> bool:
    """Check if the given user ID matches the test user ID"""
    return user_id in settings.test_user_ids