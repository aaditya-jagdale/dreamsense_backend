from fastapi import Request, HTTPException
from typing import Dict, Any, Optional
import json

class RequestValidator:
    @staticmethod
    async def parse_json_body(request: Request) -> Dict[str, Any]:
        """Parse and validate JSON request body"""
        try:
            body = await request.json()
        except ValueError as e:
            raise HTTPException(status_code=400, detail=f"Invalid JSON in request body: {str(e)}")
        
        if not isinstance(body, dict):
            raise HTTPException(status_code=400, detail="Request body must be a JSON object")
        
        return body
    
    @staticmethod
    def validate_required_field(body: Dict[str, Any], field_name: str, field_type: type = str) -> Any:
        """Validate required field exists and has correct type"""
        value = body.get(field_name)
        if value is None:
            raise HTTPException(status_code=400, detail=f"Missing required field '{field_name}'")
        
        if not isinstance(value, field_type):
            raise HTTPException(status_code=400, detail=f"Field '{field_name}' must be a {field_type.__name__}")
        
        if field_type == str and len(value.strip()) == 0:
            raise HTTPException(status_code=400, detail=f"Field '{field_name}' cannot be empty")
        
        return value
    
    @staticmethod
    def validate_string_field(body: Dict[str, Any], field_name: str, required: bool = True) -> Optional[str]:
        """Validate string field with optional requirement"""
        value = body.get(field_name)
        
        if value is None:
            if required:
                raise HTTPException(status_code=400, detail=f"Missing required field '{field_name}'")
            return None
        
        if not isinstance(value, str):
            raise HTTPException(status_code=400, detail=f"Field '{field_name}' must be a string")
        
        if required and len(value.strip()) == 0:
            raise HTTPException(status_code=400, detail=f"Field '{field_name}' cannot be empty")
        
        return value.strip() if value else value

# Global instance
request_validator = RequestValidator() 