import os
import json
from google.oauth2 import service_account
from google.auth.transport.requests import Request
import requests
import datetime
from typing import Dict, Optional, Tuple

def verify_subscription(
    package_name: str,
    subscription_id: str, 
    purchase_token: str
) -> Tuple[bool, Optional[Dict], Optional[str]]:
    try:
        # Get credentials from credentials.json
        credentials_file = "credentials.json"
        if not os.path.exists(credentials_file):
            return False, None, "Credentials file not found"
            
        credentials = service_account.Credentials.from_service_account_file(
            credentials_file,
            scopes=["https://www.googleapis.com/auth/androidpublisher"]
        )
        credentials.refresh(Request())
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
        "success": error is None,
        "expiry_date": None  # Always include expiry_date, default to None
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
