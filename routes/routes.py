import time
from fastapi import APIRouter, Request, HTTPException
from routes.send_dreams import send_dream
from typing import Dict
from routes.generate_images import generate_image
import jwt
from dotenv import load_dotenv
load_dotenv()

from services.supabase import Supabase
from services.google_cloud import check_subscription_status, get_google_credentials

router = APIRouter()
supabase = Supabase()

@router.get("/health")
async def health() -> Dict[str, str]:
    return {"message": "Never gonna give you up"}

@router.post("/send-dream")
async def handle_dream(request: Request) -> Dict:
    try:
        # Check for Authorization header
        auth_header = request.headers.get("Authorization")
        if not auth_header:
            raise HTTPException(status_code=401, detail="Authorization header is required")
            
        # Validate Bearer token format
        if not auth_header.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="Invalid authorization format. Must be 'Bearer <token>'")
        
        # Extract and validate token
        try:
            token = auth_header.split(" ")[1]
            if not token or len(token.strip()) == 0:
                raise HTTPException(status_code=401, detail="Empty token provided")
        except IndexError:
            raise HTTPException(status_code=401, detail="Malformed authorization header")

        # Verify token with Supabase
        try:
            if not supabase.verify_token(token):
                raise HTTPException(status_code=401, detail="Invalid or expired token")
        except Exception as e:
            raise HTTPException(status_code=401, detail=f"Token verification failed: {str(e)}")

        # Parse request body
        try:
            body = await request.json()
        except ValueError as e:
            raise HTTPException(status_code=400, detail=f"Invalid JSON in request body: {str(e)}")

        if not isinstance(body, dict):
            raise HTTPException(status_code=400, detail="Request body must be a JSON object")
            
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
            response = await send_dream(query, access_token=token)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to generate dream response: {str(e)}")

        # Handle image generation and upload
        if response.get('imageJsonProfile'):
            try:
                image_url = await supabase.upload_image(response['imageJsonProfile'], access_token=token)
                response["image_url"] = image_url if image_url else None
            except Exception as e:
                print(f"Image generation/upload failed: {str(e)}")
                response["image_url"] = None

        return response

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
@router.get("/generate-token")
async def generate_token(request: Request) -> Dict:
    access_token = supabase.get_access_token()
    return {"access_token": access_token}


@router.post("/generate-image")
async def gen_image(request: Request) -> Dict:
    try:
        # Check for Authorization header
        auth_header = request.headers.get("Authorization")
        if not auth_header:
            raise HTTPException(status_code=401, detail="Authorization header is required")
            
        # Validate Bearer token format
        if not auth_header.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="Invalid authorization format. Must be 'Bearer <token>'")
            
        token = auth_header.split(" ")[1]

        # Validate token and get user ID
        if not supabase.verify_token(token):
            raise HTTPException(status_code=401, detail="Invalid token")
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
            image_url = await supabase.upload_image(prompt, access_token=token)
            return {"image": image_url}
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to generate or upload image: {str(e)}")

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.get("/")
async def root() -> Dict[str, str]:
    return {"message": "Never gonna let you down"}

@router.post("/verify-subscription")
async def verify_subscription_endpoint(request: Request) -> Dict:
    try:
        # Check for Authorization header
        auth_header = request.headers.get("Authorization")
        if not auth_header:
            raise HTTPException(status_code=401, detail="Authorization header is required")
            
        # Validate Bearer token format
        if not auth_header.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="Invalid authorization format. Must be 'Bearer <token>'")
        
        # Extract and validate token
        try:
            token = auth_header.split(" ")[1]
            if not token or len(token.strip()) == 0:
                raise HTTPException(status_code=401, detail="Empty token provided")
        except IndexError:
            raise HTTPException(status_code=401, detail="Malformed authorization header")

        # Verify token with Supabase
        try:
            if not supabase.verify_token(token):
                raise HTTPException(status_code=401, detail="Invalid or expired token")
        except Exception as e:
            raise HTTPException(status_code=401, detail=f"Token verification failed: {str(e)}")

        # Parse request body
        try:
            body = await request.json()
        except ValueError as e:
            raise HTTPException(status_code=400, detail=f"Invalid JSON in request body: {str(e)}")

        if not isinstance(body, dict):
            raise HTTPException(status_code=400, detail="Request body must be a JSON object")
            
        # Validate required fields
        package_name = body.get("package_name")
        subscription_id = body.get("subscription_id")
        purchase_token = body.get("purchase_token")
        
        if not package_name:
            raise HTTPException(status_code=400, detail="Missing required field 'package_name'")
        if not subscription_id:
            raise HTTPException(status_code=400, detail="Missing required field 'subscription_id'")
        if not purchase_token:
            raise HTTPException(status_code=400, detail="Missing required field 'purchase_token'")
        
        if not isinstance(package_name, str) or not isinstance(subscription_id, str) or not isinstance(purchase_token, str):
            raise HTTPException(status_code=400, detail="All fields must be strings")

        # Validate field lengths
        if len(package_name.strip()) == 0:
            raise HTTPException(status_code=400, detail="Package name cannot be empty")
        if len(subscription_id.strip()) == 0:
            raise HTTPException(status_code=400, detail="Subscription ID cannot be empty")
        if len(purchase_token.strip()) == 0:
            raise HTTPException(status_code=400, detail="Purchase token cannot be empty")

        # Verify subscription
        try:
            subscription_status = check_subscription_status(
                package_name=package_name.strip(),
                subscription_id=subscription_id.strip(),
                purchase_token=purchase_token.strip()
            )
            
            # If verification failed, return appropriate error
            if not subscription_status["success"]:
                error_msg = subscription_status.get("error", "Unknown verification error")
                if "API Error: 401" in error_msg:
                    raise HTTPException(status_code=401, detail="Invalid Google Play credentials or insufficient permissions")
                elif "API Error: 404" in error_msg:
                    raise HTTPException(status_code=404, detail="Subscription not found. Please verify package_name, subscription_id, and purchase_token")
                else:
                    raise HTTPException(status_code=500, detail={
                        "message" : f"Subscription verification failed: {error_msg}",
                        "package_name": package_name,
                        "subscription_id": subscription_id,
                        "purchase_token": purchase_token
                    })
            
            return subscription_status
            
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail={
                "message" : f"Subscription verification failed: {str(e)}",
                "package_name": package_name,
                "subscription_id": subscription_id,
                "purchase_token": purchase_token
            })

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.get("/google-cloud-health")
async def google_cloud_health() -> Dict:
    """
    Check if Google Cloud credentials are properly configured.
    This endpoint helps verify that the environment variables are set correctly.
    """
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