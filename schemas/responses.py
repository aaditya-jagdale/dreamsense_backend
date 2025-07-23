from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime

class BaseResponse(BaseModel):
    success: bool = Field(..., description="Whether the operation was successful")
    message: str = Field(..., description="Response message")

class HealthResponse(BaseResponse):
    pass

class SendDreamResponse(BaseResponse):
    data: Optional[str] = Field(None, description="Generated dream analysis")
    image_url: Optional[str] = Field(None, description="Generated image URL")
    image_filename: Optional[str] = Field(None, description="Generated image filename")
    id: Optional[str] = Field(None, description="Dream record ID")
    supabase_data: Optional[Dict[str, Any]] = Field(None, description="Supabase record data")

class GenerateImageResponse(BaseModel):
    image: Dict[str, str] = Field(..., description="Generated image data")

class GenerateTokenResponse(BaseModel):
    access_token: str = Field(..., description="Generated access token")

class TTSResponse(BaseModel):
    CreationTime: str = Field(..., description="Creation timestamp")
    OutputUri: str = Field(..., description="URI to the generated audio file")
    RequestCharacters: int = Field(..., description="Number of characters in the request")
    TaskId: str = Field(..., description="Task ID for the TTS request")
    TaskStatus: str = Field(..., description="Status of the TTS task")
    TimestampsUri: Optional[str] = Field(None, description="URI to timestamps data")
    VoiceId: str = Field(..., description="Voice ID used for TTS")

class SubscriptionStatus(BaseModel):
    is_pro: bool = Field(..., description="Whether the user has pro subscription")
    subscription_type: str = Field(..., description="Type of subscription (pro_subscription, free_trial, test_user, etc.)")
    expiry_date: Optional[str] = Field(None, description="Subscription expiry date (ISO format)")
    dreams_remaining: Optional[int] = Field(None, description="Number of dreams remaining for free trial users")
    success: bool = Field(..., description="Whether the verification was successful")
    error: Optional[str] = Field(None, description="Error message if verification failed")
    error_type: Optional[str] = Field(None, description="Type of error that occurred")

class GoogleCloudHealthResponse(BaseModel):
    status: str = Field(..., description="Health status")
    message: str = Field(..., description="Health message")
    has_access_token: bool = Field(..., description="Whether access token is available")
    token_type: Optional[str] = Field(None, description="Token type")
    error: Optional[str] = Field(None, description="Error message if unhealthy")

class ErrorResponse(BaseModel):
    detail: str = Field(..., description="Error details") 