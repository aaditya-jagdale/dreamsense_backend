import json
import base64
from google.oauth2 import service_account
from google.auth.transport.requests import Request
from utils.config import settings

class GoogleCloudUtils:
    @staticmethod
    def get_google_credentials():
        """Get Google Cloud credentials from base64 encoded environment variable"""
        credentials_b64 = settings.google_service_account_json_b64
        
        if not credentials_b64:
            raise Exception("GOOGLE_SERVICE_ACCOUNT_JSON_B64 environment variable is required")
        
        try:
            credentials_json = base64.b64decode(credentials_b64).decode('utf-8')
            credentials_info = json.loads(credentials_json)
            credentials = service_account.Credentials.from_service_account_info(
                credentials_info, 
                scopes=["https://www.googleapis.com/auth/androidpublisher"]
            )
            credentials.refresh(Request())
            return credentials
        except Exception as e:
            raise Exception(f"Failed to decode GOOGLE_SERVICE_ACCOUNT_JSON_B64 environment variable: {e}")

    # Note: All subscription verification functions have been removed
    # as the app no longer requires purchase token validation.
    # Only JWT authentication is used now. 