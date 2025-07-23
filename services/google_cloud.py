import datetime
from typing import Dict
from services.google_cloud_utils import GoogleCloudUtils

def get_google_credentials():
    """Get Google Cloud credentials using consolidated utilities"""
    return GoogleCloudUtils.get_google_credentials()

# Note: All subscription verification functions have been removed
# as the app no longer requires purchase token validation.
# Only JWT authentication is used now.
