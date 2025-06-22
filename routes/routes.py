from fastapi import APIRouter, Request, HTTPException
from routes.send_dreams import send_dream
from typing import Dict

router = APIRouter()

@router.get("/health")
async def health() -> Dict[str, str]:
    return {"message": "Never gonna give you up"}

@router.post("/send-dream")
async def handle_dream(request: Request) -> Dict:
    try:
        body = await request.json()
        if not isinstance(body, dict):
            raise HTTPException(status_code=400, detail="Invalid request body format")
            
        query = body.get("query")
        if not query or not isinstance(query, str):
            raise HTTPException(status_code=400, detail="Query must be a non-empty string")

        response = await send_dream(query=query)
        return response

    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid JSON in request body")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.get("/")
async def root() -> Dict[str, str]:
    return {"message": "Never gonna let you down"} 