from fastapi import Request, HTTPException
from services.supabase_client import Supabase
from typing import Optional

class AuthService:
    def __init__(self):
        self.supabase = Supabase()
    
    def verify_user_token(self, request: Request) -> bool:
        """Verify user token from Authorization header"""
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return False
        
        try:
            token = auth_header.split(" ")[1]
            if not token or len(token.strip()) == 0:
                return False
            return self.supabase.verify_token(token)
        except (IndexError, Exception):
            return False
    
    def get_token_from_request(self, request: Request) -> Optional[str]:
        """Extract token from Authorization header"""
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return None
        
        try:
            return auth_header.split(" ")[1]
        except IndexError:
            return None
    
    def require_auth(self, request: Request) -> str:
        """Require authentication and return token, raises HTTPException if invalid"""
        if not self.verify_user_token(request):
            raise HTTPException(status_code=401, detail="Invalid or expired token")
        
        token = self.get_token_from_request(request)
        if not token:
            raise HTTPException(status_code=401, detail="Missing authorization token")
        
        return token

# Global instance
auth_service = AuthService() 