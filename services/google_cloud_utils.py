import json
import base64
from google.oauth2 import service_account
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import datetime
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
    def verify_subscription(package_name: str, subscription_id: str, purchase_token: str):
        """
        Verify subscription using Google Play Developer API
        """
        try:
            credentials = GoogleCloudUtils.get_google_credentials()
            service = build('androidpublisher', 'v3', credentials=credentials)
            
            # Get subscription details
            result = service.purchases().subscriptions().get(
                packageName=package_name,
                subscriptionId=subscription_id,
                token=purchase_token
            ).execute()
            
            return result
            
        except HttpError as e:
            print(f"HTTP Error in verify_subscription: {e}")
            raise Exception(f"Google Play API error: {e}")
        except Exception as e:
            print(f"Error in verify_subscription: {e}")
            raise Exception(f"Subscription verification failed: {e}")

    @staticmethod
    def check_subscription_status(package_name: str, subscription_id: str, purchase_token: str):
        """
        Check subscription status and return structured response
        """
        try:
            # Verify subscription with Google Play API
            subscription_data = GoogleCloudUtils.verify_subscription(
                package_name, subscription_id, purchase_token
            )
            
            # Extract relevant information
            expiry_time_millis = int(subscription_data.get('expiryTimeMillis', 0))
            expiry_date = datetime.datetime.fromtimestamp(expiry_time_millis / 1000, tz=datetime.UTC)
            
            # Check if subscription is active
            is_active = expiry_date > datetime.datetime.now(datetime.UTC)
            
            # Check if auto-renewing
            auto_renewing = subscription_data.get('autoRenewing', False)
            
            # Get payment state (0 = pending, 1 = purchased, 2 = free trial, 3 = pending deferred upgrade/downgrade)
            payment_state = subscription_data.get('paymentState', 0)
            
            return {
                "success": True,
                "is_active": is_active and payment_state in [1, 2],  # purchased or free trial
                "expiry_date": expiry_date.isoformat(),
                "auto_renewing": auto_renewing,
                "payment_state": payment_state,
                "raw_data": subscription_data
            }
            
        except Exception as e:
            print(f"Error checking subscription status: {e}")
            return {
                "success": False,
                "is_active": False,
                "expiry_date": None,
                "auto_renewing": False,
                "payment_state": None,
                "error": str(e)
            } 