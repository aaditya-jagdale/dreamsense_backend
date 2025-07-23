from fastapi import APIRouter, Request, HTTPException, Depends
from fastapi.responses import StreamingResponse
from routes.send_dreams import send_dream
from typing import Dict
from routes.generate_images import generate_image
from dotenv import load_dotenv
load_dotenv()

from services.supabase_client import Supabase
from services.google_cloud import get_google_credentials
from services.streaming_service import streaming_service
from utils.auth import auth_service
from utils.validators import request_validator
from schemas.requests import SendDreamRequest, GenerateImageRequest, VerifySubscriptionRequest, StreamDreamRequest
from schemas.responses import (
    HealthResponse, SendDreamResponse, GenerateImageResponse, 
    GenerateTokenResponse, SubscriptionStatus, GoogleCloudHealthResponse
)

router = APIRouter()
supabase = Supabase()

# Health check endpoint
@router.get("/health", response_model=HealthResponse)
async def health() -> HealthResponse:
    return HealthResponse(success=True, message="Never gonna give you up")

# Send a dream to the AI agent
@router.post("/send-dream", response_model=SendDreamResponse)
async def handle_dream(request: SendDreamRequest, auth_token: str = Depends(auth_service.require_auth)) -> SendDreamResponse:
    try:
        # Get user profile
        user_profile = supabase.get_user_profile(auth_token)
        
        # Generate dream response
        try:
            response = await send_dream(request.query, access_token=auth_token, user_profile=user_profile)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to generate dream response: {str(e)}")
            
        supabase_data = supabase.upload_dream(user_input=request.query, response=response["data"], access_token=auth_token)
        response['id'] = supabase_data['id']
        response['supabase_data'] = supabase_data

        return SendDreamResponse(**response)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

# Generate a dummy access token
@router.get("/generate-token", response_model=GenerateTokenResponse)
async def generate_token() -> GenerateTokenResponse:
    access_token = supabase.get_access_token()
    return GenerateTokenResponse(access_token=access_token)

# Generate an image using Gemini
@router.post("/generate-image", response_model=GenerateImageResponse)
async def gen_image(request: GenerateImageRequest, auth_token: str = Depends(auth_service.require_auth)) -> GenerateImageResponse:
    try:
        # Generate and upload image
        try:
            image_url = await supabase.upload_image(request.prompt, access_token=auth_token, user_profile={})
            return GenerateImageResponse(image=image_url)
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to generate or upload image: {str(e)}")

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

# Root endpoint
@router.get("/", response_model=HealthResponse)
async def root() -> HealthResponse:
    return HealthResponse(success=True, message="Never gonna let you down")

# Verify a subscription - simplified to just return success since no subscription checking
@router.post("/verify-subscription", response_model=SubscriptionStatus)
async def verify_subscription_endpoint(request: VerifySubscriptionRequest, auth_token: str = Depends(auth_service.require_auth)) -> SubscriptionStatus:
    try:
        # Since we're removing subscription verification, just return success
        return SubscriptionStatus(
            status="SUCCESS",
            message="No subscription verification required - all users have access"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.get("/google-cloud-health", response_model=GoogleCloudHealthResponse)
async def google_cloud_health() -> GoogleCloudHealthResponse:
    try:
        # Try to get credentials
        credentials = get_google_credentials()
        
        # Check if we can get an access token
        access_token = credentials.token
        if not access_token:
            raise Exception("No access token available")
        
        return GoogleCloudHealthResponse(
            status="healthy",
            message="Google Cloud credentials are properly configured",
            has_access_token=bool(access_token),
            token_type=type(credentials).__name__
        )
    except Exception as e:
        return GoogleCloudHealthResponse(
            status="unhealthy",
            message=f"Google Cloud credentials not properly configured: {str(e)}",
            has_access_token=False,
            error=str(e)
        ) 

# Stream dream analysis endpoint
@router.post("/stream")
async def stream_dream(request: StreamDreamRequest, auth_token: str = Depends(auth_service.require_auth)):
    """
    Stream dream analysis using Gemini LLM with real-time token streaming.
    """
    try:
        # Get user profile
        user_profile = supabase.get_user_profile(auth_token)
        
        # Create streaming response
        async def generate_stream():
            async for chunk in streaming_service.stream_dream_analysis(
                query=request.query,
                access_token=auth_token,
                user_profile=user_profile
            ):
                yield chunk
        
        return StreamingResponse(
            generate_stream(),
            media_type="text/plain",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "Content-Type": "text/plain; charset=utf-8"
            }
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
    
    