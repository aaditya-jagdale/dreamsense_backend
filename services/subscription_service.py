import datetime
from typing import Dict
from services.supabase_client import Supabase
from services.google_cloud_utils import GoogleCloudUtils
from utils.config import settings

class SubscriptionService:
    def __init__(self):
        self.supabase = Supabase()
        self.package_name = settings.package_name
        self.subscription_id = settings.subscription_id
    
    def check_subscription(self, purchase_token: str, access_token: str) -> Dict:
        """
        Check if user has a pro subscription using the purchase token.
        Returns a dictionary with subscription status information.
        """
        try:
            # Get user ID from token
            user_id = self.supabase.get_user_id(access_token)
            print(f"Checking subscription for user_id: {user_id}")
            print(f"Purchase token: {purchase_token}")
            
            # Check subscription status using Google Play API
            subscription_result = GoogleCloudUtils.check_subscription_status(
                package_name=self.package_name,
                subscription_id=self.subscription_id,
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
            dream_count = self.supabase.get_user_dream_count(access_token)
            dreams_remaining = max(0, settings.free_trial_dreams - dream_count) if isinstance(dream_count, int) else 0
            
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
            print(f"Error in check_subscription: {e}")
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
    
    def format_subscription_response(self, subscription_result: Dict) -> Dict:
        """Format subscription result into consistent API response"""
        if not subscription_result.get("success", True):
            error_type = subscription_result.get("error_type", "unknown_error")
            error_msg = subscription_result.get("error", "Unknown error occurred")
            
            if error_type == "credential_loading_failed":
                return {
                    "status": "CREDENTIAL_ERROR",
                    "message": f"Failed to load Google Cloud credentials: {error_msg}",
                    "expiry_date": None,
                    "dreams_remaining": 0,
                    "is_pro": False,
                    "error_type": error_type,
                    "response": subscription_result
                }
            elif error_type == "subscription_verification_failed":
                return {
                    "status": "VERIFICATION_ERROR",
                    "message": f"Failed to verify subscription with Google Play: {error_msg}",
                    "expiry_date": None,
                    "dreams_remaining": 0,
                    "is_pro": False,
                    "error_type": error_type,
                    "response": subscription_result
                }
            else:
                return {
                    "status": "ERROR",
                    "message": f"Subscription verification error: {error_msg}",
                    "expiry_date": None,
                    "dreams_remaining": 0,
                    "is_pro": False,
                    "error_type": error_type,
                    "response": subscription_result
                }
        
        # Determine subscription status and return appropriate response
        subscription_type = subscription_result.get("subscription_type", "unknown")
        expiry_date = subscription_result.get("expiry_date")
        
        if subscription_type == "pro_subscription" and subscription_result["is_pro"]:
            return {
                "status": "Pro",
                "message": "User has an active PRO subscription",
                "expiry_date": expiry_date,
                "dreams_remaining": None,  # Pro users have unlimited dreams
                "is_pro": subscription_result["is_pro"],
                "response": subscription_result
            }
        elif subscription_type == "free_trial":
            dreams_remaining = subscription_result.get("dreams_remaining", 0)
            return {
                "status": "FREE TRIAL",
                "message": f"User has free trial access with {dreams_remaining} dreams remaining",
                "expiry_date": expiry_date,
                "dreams_remaining": dreams_remaining,
                "is_pro": subscription_result["is_pro"],
                "response": subscription_result
            }
        else:
            return {
                "status": "NO SUBSCRIPTION",
                "message": "User does not have an active subscription",
                "expiry_date": expiry_date,
                "dreams_remaining": 0,
                "is_pro": subscription_result["is_pro"],
                "response": subscription_result
            }

# Global instance
subscription_service = SubscriptionService() 