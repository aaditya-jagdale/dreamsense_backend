import os
import json
from google.oauth2 import service_account
from google.auth.transport.requests import Request
from google.auth import default
import requests
import datetime
from typing import Dict, Optional, Tuple

def get_google_credentials():
    # Check if credentials are provided as environment variable convert to json
    credentials_json = os.getenv('GOOGLE_SERVICE_ACCOUNT_JSON')
    credentials_b64 = os.getenv('GOOGLE_SERVICE_ACCOUNT_JSON_B64')
    
    if credentials_json:
        # Parse JSON from environment variable
        try:
            credentials_info = json.loads(credentials_json)
            credentials = service_account.Credentials.from_service_account_info(
                credentials_info, 
                scopes=["https://www.googleapis.com/auth/androidpublisher"]
            )
            credentials.refresh(Request())
            return credentials
        except json.JSONDecodeError:
            raise ValueError("Invalid JSON in GOOGLE_SERVICE_ACCOUNT_JSON environment variable")
    
    if credentials_b64:
        # Parse base64 encoded JSON from environment variable
        try:
            import base64
            credentials_json = base64.b64decode(credentials_b64).decode('utf-8')
            credentials_info = json.loads(credentials_json)
            credentials = service_account.Credentials.from_service_account_info(
                credentials_info, 
                scopes=["https://www.googleapis.com/auth/androidpublisher"]
            )
            credentials.refresh(Request())
            return credentials
        except Exception as e:
            raise ValueError(f"Invalid base64 encoded JSON in GOOGLE_SERVICE_ACCOUNT_JSON_B64 environment variable: {e}")
    
    # Fallback to default credentials (for Google Cloud environments)
    try:
        credentials, project = default(scopes=["https://www.googleapis.com/auth/androidpublisher"])
        return credentials
    except Exception as e:
        raise Exception(f"Failed to get default credentials: {e}")

def verify_subscription(
    package_name: str,
    subscription_id: str,
    purchase_token: str
) -> Tuple[bool, Optional[Dict], Optional[str]]:
    try:
        # Get credentials
        credentials = get_google_credentials()
        access_token = credentials.token
        
        # Build API URL
        url = f"https://androidpublisher.googleapis.com/androidpublisher/v3/applications/{package_name}/purchases/subscriptions/{subscription_id}/tokens/{purchase_token}"
        
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Accept": "application/json"
        }
        
        # Make API request
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            expiry = int(data.get("expiryTimeMillis", 0))
            expiry_date = datetime.datetime.fromtimestamp(expiry / 1000)
            now = datetime.datetime.utcnow()
            
            is_active = expiry_date > now
            
            return is_active, data, None
        else:
            error_msg = f"API Error: {response.status_code} - {response.text}"
            return False, None, error_msg
            
    except Exception as e:
        error_msg = f"Verification failed: {str(e)}"
        return False, None, error_msg

def check_subscription_status(
    package_name: str,
    subscription_id: str,
    purchase_token: str
) -> Dict:
    is_active, subscription_data, error = verify_subscription(
        package_name, subscription_id, purchase_token
    )
    
    result = {
        "is_active": is_active,
        "success": error is None
    }
    
    if error:
        result["error"] = error
    else:
        result["subscription_data"] = subscription_data
        
        if subscription_data:
            expiry = int(subscription_data.get("expiryTimeMillis", 0))
            if expiry > 0:
                expiry_date = datetime.datetime.fromtimestamp(expiry / 1000)
                result["expiry_date"] = expiry_date.isoformat()
                result["expiry_timestamp"] = expiry
    
    return result
