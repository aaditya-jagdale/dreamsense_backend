import time
from fastapi import APIRouter, Request, HTTPException
from routes.send_dreams import send_dream
from typing import Dict
from routes.generate_images import generate_image
import jwt

from services.supabase import Supabase

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
            response = await send_dream(query)
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