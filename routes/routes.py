import time
from fastapi import APIRouter, Request, HTTPException
from routes.send_dreams import send_dream
from typing import Dict
from routes.generate_images import generate_image
import jwt
from dotenv import load_dotenv
load_dotenv()

from services.supabase import Supabase
from services.google_cloud import check_subscription_status, get_google_credentials, is_pro_subscriber

router = APIRouter()
supabase = Supabase()

def verify_user_token(request: Request) -> bool:
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        return False
    
    try:
        token = auth_header.split(" ")[1]
        if not token or len(token.strip()) == 0:
            return False
        return supabase.verify_token(token)
    except (IndexError, Exception):
        return False

# Health check endpoint
@router.get("/health")
async def health() -> Dict[str, str]:
    return {"message": "Never gonna give you up"}

# Send a dream to the AI agent
@router.post("/send-dream")
async def handle_dream(request: Request) -> Dict:
    try:
        # Verify user token
        if not verify_user_token(request):
            raise HTTPException(status_code=401, detail="Invalid or expired token")

        # Get token for further use
        auth_header = request.headers.get("Authorization")
        token = auth_header.split(" ")[1]

        # Parse request body first
        try:
            body = await request.json()
        except ValueError as e:
            raise HTTPException(status_code=400, detail=f"Invalid JSON in request body: {str(e)}")

        if not isinstance(body, dict):
            raise HTTPException(status_code=400, detail="Request body must be a JSON object")

        # Check if user has a subscription
        # Note: This is a placeholder - you'll need to get the actual purchase_token from the request
        # For now, using a default value. You should modify this to get the token from the request body
        purchase_token = body.get("purchase_token", "com.dreamsense.app.subscription")
        
        is_subscriber = is_pro_subscriber(purchase_token, token)
        subscription_type = is_subscriber.get("subscription_type", "unknown")
        
        # Allow access for pro subscribers and free trial users with remaining dreams
        if not is_subscriber["is_pro"]:
            error_details = {
                "error": "subscription_required",
                "message": "User does not have an active subscription",
                "subscription_type": subscription_type,
                "purchase_token": purchase_token,
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
        user_profile = supabase.get_user_profile(token)
        
        # Validate query parameter
        query = body.get("query")
        if query is None:
            raise HTTPException(status_code=400, detail="Missing required field 'query'")
        if not isinstance(query, str):
            raise HTTPException(status_code=400, detail="Field 'query' must be a string")
        if len(query.strip()) == 0:
            raise HTTPException(status_code=400, detail="Field 'query' cannot be empty")

        # Generate dream response
        try:
            user_profile = supabase.get_user_profile(token)
            response = await send_dream(query, access_token=token, user_profile=user_profile)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to generate dream response: {str(e)}")

        # Handle image generation and upload
        if response.get('imageJsonProfile'):
            try:
                image_response = await supabase.upload_image(response['imageJsonProfile'], access_token=token, user_profile=user_profile)
                response["image_url"] = image_response["signed_url"] if image_response else None
                response["image_filename"] = image_response["filename"] if image_response else None
                
            except Exception as e:
                print(f"Image generation/upload failed: {str(e)}")
                response["image_url"] = None
                response["image_filename"] = None
            
            supabase_data = supabase.upload_dream(user_input=query, response=response["data"], image_url=response["image_filename"], access_token=token)
            response['id'] = supabase_data['id']
            response['supabase_data'] = supabase_data

        return response

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

# Generate a dummy access token
@router.get("/generate-token")
async def generate_token(request: Request) -> Dict:
    access_token = supabase.get_access_token()
    return {"access_token": access_token}

# Generate an image using Gemini
@router.post("/generate-image")
async def gen_image(request: Request) -> Dict:
    try:
        # Verify user token
        if not verify_user_token(request):
            raise HTTPException(status_code=401, detail="Invalid or expired token")

        # Get token for further use
        auth_header = request.headers.get("Authorization")
        token = auth_header.split(" ")[1]

        # Parse and validate request body
        try:
            body = await request.json()
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid JSON in request body")

        prompt = body.get("prompt")
        if not prompt:
            raise HTTPException(status_code=400, detail="Prompt is required")
        if not isinstance(prompt, str):
            raise HTTPException(status_code=400, detail="Prompt must be a string")
        if len(prompt.strip()) == 0:
            raise HTTPException(status_code=400, detail="Prompt cannot be empty")
        
        # Generate and upload image
        try:
            image_url = await supabase.upload_image(prompt, access_token=token, user_profile={})
            return {"image": image_url}
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to generate or upload image: {str(e)}")

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

# Root endpoint
@router.get("/")
async def root() -> Dict[str, str]:
    return {"message": "Never gonna let you down"}

# Verify a subscription
@router.post("/verify-subscription")
async def verify_subscription_endpoint(request: Request) -> Dict:
    try:
        # Verify user token
        if not verify_user_token(request):
            raise HTTPException(status_code=401, detail="Invalid or expired token")

        # Parse request body
        try:
            body = await request.json()
        except ValueError as e:
            raise HTTPException(status_code=400, detail=f"Invalid JSON in request body: {str(e)}")

        if not isinstance(body, dict):
            raise HTTPException(status_code=400, detail="Request body must be a JSON object")
        
        # Validate required field
        purchase_token = body.get("purchase_token")
        
        if not purchase_token:
            raise HTTPException(status_code=400, detail="Missing required field 'purchase_token'")
        
        if not isinstance(purchase_token, str):
            raise HTTPException(status_code=400, detail="Purchase token must be a string")

        # Validate field length
        if len(purchase_token.strip()) == 0:
            raise HTTPException(status_code=400, detail="Purchase token cannot be empty")

        # Verify subscription using the simple checker
        try:
            auth_header = request.headers.get("Authorization")
            token = auth_header.split(" ")[1]
            is_subscriber = is_pro_subscriber(purchase_token.strip(), token)
            
            # Determine subscription status and return appropriate response
            subscription_type = is_subscriber.get("subscription_type", "unknown")
            
            # Always include expiry_date in response, even if None
            expiry_date = is_subscriber.get("expiry_date")
            
            if subscription_type == "pro_subscription" and is_subscriber["is_pro"]:
                return {
                    "status": "Pro",
                    "message": "User has an active PRO subscription",
                    "expiry_date": expiry_date,
                    "dreams_remaining": None,  # Pro users have unlimited dreams
                    "is_pro": is_subscriber["is_pro"],
                    "response": is_subscriber
                }
            elif subscription_type == "free_trial":
                dreams_remaining = is_subscriber.get("dreams_remaining", 0)
                return {
                    "status": "FREE TRIAL",
                    "message": f"User has free trial access with {dreams_remaining} dreams remaining",
                    "expiry_date": expiry_date,
                    "dreams_remaining": dreams_remaining,
                    "is_pro": is_subscriber["is_pro"],
                    "response": is_subscriber
                }
            else:
                return {
                    "status": "NO SUBSCRIPTION",
                    "message": "User does not have an active subscription",
                    "expiry_date": expiry_date,
                    "dreams_remaining": 0,
                    "is_pro": is_subscriber["is_pro"],
                    "response": is_subscriber
                    }
            
        except Exception as e:
            raise HTTPException(status_code=500, detail={
                "message" : f"Subscription verification failed: {str(e)}",
                "purchase_token": purchase_token
            })

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.get("/google-cloud-health")
async def google_cloud_health() -> Dict:
    try:
        # Try to get credentials
        credentials = get_google_credentials()
        
        # Check if we can get an access token
        access_token = credentials.token
        if not access_token:
            raise Exception("No access token available")
        
        return {
            "status": "healthy",
            "message": "Google Cloud credentials are properly configured",
            "has_access_token": bool(access_token),
            "token_type": type(credentials).__name__
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "message": f"Google Cloud credentials not properly configured: {str(e)}",
            "has_access_token": False,
            "error": str(e)
        } 