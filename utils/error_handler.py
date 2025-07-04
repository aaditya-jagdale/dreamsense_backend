from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse
from typing import Union, Dict, Any
import logging

logger = logging.getLogger(__name__)

class ErrorHandler:
    @staticmethod
    def handle_validation_error(exc: Exception) -> JSONResponse:
        """Handle Pydantic validation errors"""
        return JSONResponse(
            status_code=422,
            content={
                "detail": "Validation error",
                "message": str(exc),
                "type": "validation_error"
            }
        )
    
    @staticmethod
    def handle_http_exception(exc: HTTPException) -> JSONResponse:
        """Handle HTTP exceptions"""
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "detail": exc.detail,
                "type": "http_error"
            }
        )
    
    @staticmethod
    def handle_generic_exception(exc: Exception) -> JSONResponse:
        """Handle generic exceptions"""
        logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={
                "detail": "Internal server error",
                "message": "An unexpected error occurred",
                "type": "internal_error"
            }
        )
    
    @staticmethod
    def format_error_response(
        status_code: int,
        message: str,
        error_type: str = "error",
        details: Union[Dict[str, Any], None] = None
    ) -> Dict[str, Any]:
        """Format error response consistently"""
        response = {
            "success": False,
            "message": message,
            "type": error_type
        }
        
        if details:
            response["details"] = details
            
        return response

# Global instance
error_handler = ErrorHandler() 