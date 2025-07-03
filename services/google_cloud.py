import os
import json
from google.oauth2 import service_account
from google.auth.transport.requests import Request
from google.auth import default
import requests
import datetime
from typing import Dict, Optional, Tuple
from services.supabase import Supabase
from services.purchase_verification import check_subscription_status

supabase = Supabase()


def get_google_credentials():
    # First, check if credentials are provided as environment variables (for production)
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
    
    # Fallback to local credentials.json file (for development)
    credentials_file = "credentials.json"
    if os.path.exists(credentials_file):
        try:
            credentials = service_account.Credentials.from_service_account_file(
                credentials_file,
                scopes=["https://www.googleapis.com/auth/androidpublisher"]
            )
            credentials.refresh(Request())
            return credentials
        except Exception as e:
            print(f"Warning: Failed to load credentials from {credentials_file}: {e}")
    
    # Final fallback to default credentials (for Google Cloud environments)
    try:
        credentials, project = default(scopes=["https://www.googleapis.com/auth/androidpublisher"])
        return credentials
    except Exception as e:
        raise Exception(f"Failed to get credentials. Please ensure you have either:\n1. GOOGLE_SERVICE_ACCOUNT_JSON environment variable set (recommended for production)\n2. GOOGLE_SERVICE_ACCOUNT_JSON_B64 environment variable set (recommended for production)\n3. A 'credentials.json' file in the project root (for development only)\n4. Default Google Cloud credentials configured\n\nError: {e}")

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

        # log the response in console
        print(response.json())
        
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

def is_pro_subscriber(purchase_token: str, access_token: str) -> Dict:
    """
    Check if user has a pro subscription using the purchase token.
    Returns a dictionary with subscription status information.
    """
    try:
        # Get user ID from token
        user_id = supabase.get_user_id(access_token)
        
        # Default package name and subscription ID for the app
        package_name = "com.dreamsense.app"
        subscription_id = "dreamsense_pro_1"
        
        # Check subscription status using Google Play API
        subscription_result = check_subscription_status(
            package_name=package_name,
            subscription_id=subscription_id,
            purchase_token=purchase_token
        )
        
        # Get user's dream count for free tier logic
        dream_count = supabase.get_user_dream_count(access_token)
        dreams_remaining = max(0, 2 - dream_count) if isinstance(dream_count, int) else 0
        
        # Determine subscription type and status
        if subscription_result.get("is_active", False):
            return {
                "is_pro": True,
                "subscription_type": "pro_subscription",
                "expiry_date": subscription_result.get("expiry_date"),
                "dreams_remaining": None,  # Pro users have unlimited dreams
                "success": True
            }
        elif dreams_remaining > 0:
            return {
                "is_pro": False,
                "subscription_type": "free_trial",
                "expiry_date": subscription_result.get("expiry_date"),
                "dreams_remaining": dreams_remaining,
                "success": True
            }
        else:
            return {
                "is_pro": False,
                "subscription_type": "no_subscription",
                "expiry_date": subscription_result.get("expiry_date"),
                "dreams_remaining": 0,
                "success": True
            }
            
    except Exception as e:
        return {
            "is_pro": False,
            "subscription_type": "error",
            "expiry_date": None,
            "dreams_remaining": 0,
            "success": False,
            "error": str(e)
        }
