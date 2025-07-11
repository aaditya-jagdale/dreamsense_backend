import base64
import json
from urllib.parse import unquote
from fastapi import Request, HTTPException
from services.supabase_client import Supabase
from typing import Optional

class AuthService:
    def __init__(self):
        self.supabase = Supabase()
    
    def verify_user_token(self, request: Request) -> bool:
        """Verify user token from Authorization header"""
        auth_header = request.headers.get("Authorization")
        print(f"Auth header: {auth_header}")
        
        if not auth_header or not auth_header.startswith("Bearer "):
            print("No Authorization header or invalid format")
            return False
        
        try:
            token = auth_header.split(" ")[1]
            if not token or len(token.strip()) == 0:
                print("Empty token")
                return False
            
            # Try URL decoding in case the token is URL-encoded
            original_token = token
            token = unquote(token)
            if token != original_token:
                print("Token was URL-encoded, decoded it")
            
            print(f"Token length: {len(token)} characters")
            print(f"Token starts with: {token[:50]}...")
            print(f"Token ends with: ...{token[-20:]}")
            
            # Check if token looks like a valid JWT (should have 3 parts separated by dots)
            parts = token.split('.')
            print(f"JWT parts count: {len(parts)}")
            if len(parts) != 3:
                print(f"Invalid JWT structure - expected 3 parts, got {len(parts)}")
                return False
            
            # Print the lengths of each part
            for i, part in enumerate(parts):
                print(f"Part {i+1} length: {len(part)}")
            
            # Check if the signature part (3rd part) looks complete
            if len(parts) >= 3:
                signature_part = parts[2]
                print(f"Signature part length: {len(signature_part)}")
                print(f"Signature part ends with: {signature_part[-10:]}")
                # A typical JWT signature should be at least 43 characters (base64 encoded)
                if len(signature_part) < 43:
                    print("WARNING: Signature part seems too short, token might be truncated")
            
            # Try to decode the header (first part) to see if it's valid
            try:
                header_part = parts[0]
                # Add padding if needed
                header_part += '=' * (4 - len(header_part) % 4) if len(header_part) % 4 else ''
                header_decoded = base64.urlsafe_b64decode(header_part).decode('utf-8')
                header_json = json.loads(header_decoded)
                print(f"JWT header: {header_json}")
            except Exception as e:
                print(f"Failed to decode JWT header: {e}")
            
            result = self.supabase.verify_token(token)
            print(f"Token verification result: {result}")
            return result
        except (IndexError, Exception) as e:
            print(f"Exception in verify_user_token: {e}")
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
        print("=== AUTHENTICATION DEBUG ===")
        print(f"Request headers: {dict(request.headers)}")
        
        if not self.verify_user_token(request):
            print("Token verification failed")
            raise HTTPException(status_code=401, detail="Invalid or expired token")
        
        token = self.get_token_from_request(request)
        if not token:
            print("No token extracted from request")
            raise HTTPException(status_code=401, detail="Missing authorization token")
        
        print("Authentication successful")
        return token

# Global instance
auth_service = AuthService() 