import json
import base64
from google.oauth2 import service_account
from google.auth.transport.requests import Request
import requests
import datetime
from typing import Dict, Optional, Tuple
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
    
    @staticmethod
    def verify_subscription(
        package_name: str,
        subscription_id: str,
        purchase_token: str
    ) -> Tuple[bool, Optional[Dict], Optional[str]]:
        """Verify subscription with Google Play API"""
        try:
            credentials = GoogleCloudUtils.get_google_credentials()
            access_token = credentials.token
            
            url = f"https://androidpublisher.googleapis.com/androidpublisher/v3/applications/{package_name}/purchases/subscriptions/{subscription_id}/tokens/{purchase_token}"
            
            headers = {
                "Authorization": f"Bearer {access_token}",
                "Accept": "application/json"
            }
            
            response = requests.get(url, headers=headers)
            print(f"Google Play API Response: {response.json()}")
            
            if response.status_code == 200:
                data = response.json()
                expiry = int(data.get("expiryTimeMillis", 0))
                expiry_date = datetime.datetime.fromtimestamp(expiry / 1000, datetime.UTC)
                now = datetime.datetime.now(datetime.UTC)
                
                is_active = expiry_date > now
                return is_active, data, None
            else:
                error_msg = f"API Error: {response.status_code} - {response.text}"
                return False, None, error_msg
                
        except Exception as e:
            error_msg = f"Verification failed: {str(e)}"
            return False, None, error_msg
    
    @staticmethod
    def check_subscription_status(
        package_name: str,
        subscription_id: str,
        purchase_token: str
    ) -> Dict:
        """Check subscription status and return formatted result"""
        is_active, subscription_data, error = GoogleCloudUtils.verify_subscription(
            package_name, subscription_id, purchase_token
        )
        
        result = {
            "is_active": is_active,
            "success": error is None,
            "expiry_date": None
        }
        
        if error:
            result["error"] = error
        else:
            result["subscription_data"] = subscription_data
            
            if subscription_data:
                expiry = int(subscription_data.get("expiryTimeMillis", 0))
                if expiry > 0:
                    expiry_date = datetime.datetime.fromtimestamp(expiry / 1000, datetime.UTC)
                    result["expiry_date"] = expiry_date.isoformat()
                    result["expiry_timestamp"] = expiry
        
        return result 