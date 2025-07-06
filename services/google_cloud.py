import datetime
from typing import Dict
from services.supabase_client import Supabase
from services.google_cloud_utils import GoogleCloudUtils
from utils.config import Settings

supabase = Supabase()
settings = Settings()

def get_google_credentials():
    """Get Google Cloud credentials using consolidated utilities"""
    return GoogleCloudUtils.get_google_credentials()

def verify_subscription(
    package_name: str,
    subscription_id: str,
    purchase_token: str
):
    """Verify subscription using consolidated utilities"""
    return GoogleCloudUtils.verify_subscription(package_name, subscription_id, purchase_token)

def is_pro_subscriber(purchase_token: str, access_token: str) -> Dict:
    """
    Check if user has a pro subscription using the purchase token.
    Returns a dictionary with subscription status information.
    """
    try:
        # Get user ID from token
        user_id = supabase.get_user_id(access_token)
        print(f"Checking subscription for user_id: {user_id}")
        print(f"Purchase token: {purchase_token}")
        
        # Default package name and subscription ID for the app
        package_name = settings.package_name
        subscription_id = settings.subscription_id
        
        print(f"Checking subscription with package_name: {package_name}, subscription_id: {subscription_id}")
        
        # Check subscription status using Google Play API
        subscription_result = GoogleCloudUtils.check_subscription_status(
            package_name=package_name,
            subscription_id=subscription_id,
            purchase_token=purchase_token
        )
        
        print(f"Subscription result: {subscription_result}")
        
        # Check if there was an error in subscription verification
        if not subscription_result.get("success", False):
            error_msg = subscription_result.get("error", "Unknown subscription verification error")
            print(f"Subscription verification failed: {error_msg}")
            return {
                "is_pro": False,
                "subscription_type": "verification_error",
                "expiry_date": None,
                "dreams_remaining": 0,
                "success": False,
                "error": error_msg,
                "error_type": "subscription_verification_failed"
            }
        
        # Get user's dream count for free tier logic
        dream_count = supabase.get_user_dream_count(access_token)
        dreams_remaining = max(0, 2 - dream_count) if isinstance(dream_count, int) else 0
        
        print(f"Dream count: {dream_count}, Dreams remaining: {dreams_remaining}")
        
        # Determine subscription type and status
        if subscription_result.get("is_active", False):
            expiry_date_str = subscription_result.get("expiry_date")
            if expiry_date_str:
                try:
                    expiry_date = datetime.datetime.fromisoformat(expiry_date_str)
                    if expiry_date > datetime.datetime.now(datetime.UTC):
                        print("User has active PRO subscription")
                        return {
                            "is_pro": True,
                            "subscription_type": "pro_subscription",
                            "expiry_date": expiry_date_str,
                            "dreams_remaining": None,  # Pro users have unlimited dreams
                            "success": True
                        }
                    else:
                        print(f"Subscription expired on {expiry_date}")
                except Exception as e:
                    print(f"Error parsing expiry date: {e}")
            else:
                print("No expiry date found in subscription result")
        
        # Check for free trial
        if dreams_remaining > 0:
            print(f"User has free trial with {dreams_remaining} dreams remaining")
            return {
                "is_pro": True,  # Free trial users should return TRUE
                "subscription_type": "free_trial",
                "expiry_date": subscription_result.get("expiry_date"),
                "dreams_remaining": dreams_remaining,
                "success": True
            }
        else:
            print("User has no active subscription or free trial")
            return {
                "is_pro": False,
                "subscription_type": "no_subscription",
                "expiry_date": subscription_result.get("expiry_date"),
                "dreams_remaining": 0,
                "success": True
            }
            
    except Exception as e:
        print(f"Error in is_pro_subscriber: {e}")
        # Check if it's a credential-related error
        if "GOOGLE_SERVICE_ACCOUNT_JSON_B64" in str(e) or "Failed to decode" in str(e):
            return {
                "is_pro": False,
                "subscription_type": "credential_error",
                "expiry_date": None,
                "dreams_remaining": 0,
                "success": False,
                "error": str(e),
                "error_type": "credential_loading_failed"
            }
        else:
            return {
                "is_pro": False,
                "subscription_type": "error",
                "expiry_date": None,
                "dreams_remaining": 0,
                "success": False,
                "error": str(e),
                "error_type": "general_error"
            }
