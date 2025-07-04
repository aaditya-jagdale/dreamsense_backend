from pydantic import BaseModel, Field, validator
from typing import Optional

class SendDreamRequest(BaseModel):
    query: str = Field(..., description="The dream description to analyze", min_length=1)
    purchase_token: Optional[str] = Field(
        default="com.dreamsense.app.subscription", 
        description="Purchase token for subscription verification"
    )
    
    @validator('query')
    def validate_query(cls, v):
        if not v or not v.strip():
            raise ValueError('Query cannot be empty')
        return v.strip()

class GenerateImageRequest(BaseModel):
    prompt: str = Field(..., description="Image generation prompt", min_length=1)
    
    @validator('prompt')
    def validate_prompt(cls, v):
        if not v or not v.strip():
            raise ValueError('Prompt cannot be empty')
        return v.strip()

class VerifySubscriptionRequest(BaseModel):
    purchase_token: str = Field(..., description="Purchase token to verify", min_length=1)
    
    @validator('purchase_token')
    def validate_purchase_token(cls, v):
        if not v or not v.strip():
            raise ValueError('Purchase token cannot be empty')
        return v.strip()

class TTSRequest(BaseModel):
    text: str = Field(..., description="Text to convert to speech", min_length=1)
    
    @validator('text')
    def validate_text(cls, v):
        if not v or not v.strip():
            raise ValueError('Text cannot be empty')
        return v.strip() 