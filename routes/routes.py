from fastapi import APIRouter, Request, HTTPException, Depends
from routes.send_dreams import send_dream
from typing import Dict
from routes.generate_images import generate_image
from dotenv import load_dotenv
load_dotenv()

from services.supabase_client import Supabase
from services.google_cloud import get_google_credentials
from services.subscription_service import subscription_service
from utils.auth import auth_service
from utils.validators import request_validator
from schemas.requests import SendDreamRequest, GenerateImageRequest, VerifySubscriptionRequest
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
        # Check if user has a subscription
        is_subscriber = subscription_service.check_subscription(request.purchase_token, auth_token)
        subscription_type = is_subscriber.get("subscription_type", "unknown")
        
        # Allow access for pro subscribers and free trial users with remaining dreams
        if not is_subscriber["is_pro"]:
            error_details = {
                "error": "subscription_required",
                "message": "User does not have an active subscription",
                "subscription_type": subscription_type,
                "purchase_token": request.purchase_token,
                "is_pro": is_subscriber["is_pro"],
                "expiry_date": is_subscriber.get("expiry_date"),
                "dreams_remaining": is_subscriber.get("dreams_remaining")
            }
            
            if subscription_type == "no_subscription":
                error_details["message"] = "User does not have a subscription"
            else:
                # Handle other cases like expired subscriptions
                error_msg = is_subscriber.get("error", "Subscription verification failed")
                error_details["message"] = f"Subscription error: {error_msg}"
            
            print(f"Subscription verification failed in send-dream: {error_details}")
            raise HTTPException(status_code=403, detail=error_details)
        
        # Get user profile
        user_profile = supabase.get_user_profile(auth_token)
        
        # Generate dream response
        try:
            response = await send_dream(request.query, access_token=auth_token, user_profile=user_profile)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to generate dream response: {str(e)}")

        # Handle image generation and upload
        if response.get('imageJsonProfile'):
            try:
                image_response = await supabase.upload_image(response['imageJsonProfile'], access_token=auth_token, user_profile=user_profile)
                response["image_url"] = image_response["signed_url"] if image_response else None
                response["image_filename"] = image_response["filename"] if image_response else None
                
            except Exception as e:
                print(f"Image generation/upload failed: {str(e)}")
                response["image_url"] = None
                response["image_filename"] = None
            
            supabase_data = supabase.upload_dream(user_input=request.query, response=response["data"], image_url=response["image_filename"], access_token=auth_token)
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

# Verify a subscription
@router.post("/verify-subscription", response_model=SubscriptionStatus)
async def verify_subscription_endpoint(request: VerifySubscriptionRequest, auth_token: str = Depends(auth_service.require_auth)) -> SubscriptionStatus:
    try:
        # Verify subscription using the subscription service
        is_subscriber = subscription_service.check_subscription(request.purchase_token, auth_token)
        
        # Format the response using the subscription service
        formatted_response = subscription_service.format_subscription_response(is_subscriber)
        
        return SubscriptionStatus(**formatted_response)
        
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