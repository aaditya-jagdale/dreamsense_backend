from services.google_cloud_utils import GoogleCloudUtils

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

def check_subscription_status(
    package_name: str,
    subscription_id: str,
    purchase_token: str
):
    """Check subscription status using consolidated utilities"""
    return GoogleCloudUtils.check_subscription_status(package_name, subscription_id, purchase_token)
