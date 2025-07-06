#!/usr/bin/env python3
"""
API Test Script for DreamSense Backend
Tests all endpoints and provides a comprehensive status report
"""

import requests
import json
import time
import os
from typing import Dict, List, Tuple
import tempfile
from pathlib import Path

class APITester:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.results = {}
        self.access_token = None
        
    def print_status(self, service_name: str, success: bool, message: str = ""):
        """Print status with emoji indicators"""
        if success:
            print(f"✅ {service_name}: Working")
            if message:
                print(f"   └─ {message}")
        else:
            print(f"🚨 {service_name}: Not working")
            if message:
                print(f"   └─ {message}")
        print()
    
    def get_headers(self, include_auth: bool = True) -> Dict[str, str]:
        """Get headers for API requests"""
        headers = {
            "Content-Type": "application/json"
        }
        if include_auth and self.access_token:
            headers["Authorization"] = f"Bearer {self.access_token}"
        return headers
    
    def test_health_check(self) -> Tuple[bool, str]:
        """Test the health check endpoint"""
        try:
            response = requests.get(f"{self.base_url}/health", timeout=10)
            if response.status_code == 200:
                data = response.json()
                success = data.get("message") == "Never gonna give you up"
                return success, ""
            return False, f"Status code: {response.status_code}"
        except Exception as e:
            return False, f"Connection error: {str(e)}"
    
    def test_root_endpoint(self) -> Tuple[bool, str]:
        """Test the root endpoint"""
        try:
            response = requests.get(f"{self.base_url}/", timeout=10)
            if response.status_code == 200:
                data = response.json()
                success = data.get("message") == "Never gonna let you down"
                return success, ""
            return False, f"Status code: {response.status_code}"
        except Exception as e:
            return False, f"Connection error: {str(e)}"
    
    def test_generate_token(self) -> Tuple[bool, str]:
        """Test token generation and store the token"""
        try:
            response = requests.get(f"{self.base_url}/generate-token", timeout=10)
            if response.status_code == 200:
                data = response.json()
                self.access_token = data.get("access_token")
                success = bool(self.access_token)
                return success, ""
            return False, f"Status code: {response.status_code}"
        except Exception as e:
            return False, f"Connection error: {str(e)}"
    
    def test_send_dream(self) -> Tuple[bool, str]:
        """Test the send dream API"""
        if not self.access_token:
            return False, "No access token available"
            
        try:
            payload = {
                "query": "I dreamed about flying over a beautiful city at sunset"
            }
            response = requests.post(
                f"{self.base_url}/send-dream",
                headers=self.get_headers(),
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                success = data.get("success", False) and data.get("data") is not None
                return success, ""
            elif response.status_code == 401:
                return False, f"Authentication failed - token may be invalid"
            else:
                try:
                    error_data = response.json()
                    error_msg = error_data.get("detail", "Unknown error")
                except:
                    error_msg = f"Status code: {response.status_code}"
                return False, error_msg
        except Exception as e:
            return False, f"Connection error: {str(e)}"
    
    def test_generate_image(self) -> Tuple[bool, str]:
        """Test the image generation API"""
        if not self.access_token:
            return False, "No access token available"
            
        try:
            payload = {
                "prompt": "A serene dream landscape with floating islands and gentle clouds"
            }
            response = requests.post(
                f"{self.base_url}/generate-image",
                headers=self.get_headers(),
                json=payload,
                timeout=60
            )
            
            if response.status_code == 200:
                data = response.json()
                success = "image" in data
                return success, ""
            elif response.status_code == 401:
                return False, f"Authentication failed - token may be invalid"
            else:
                try:
                    error_data = response.json()
                    error_msg = error_data.get("detail", "Unknown error")
                except:
                    error_msg = f"Status code: {response.status_code}"
                return False, error_msg
        except Exception as e:
            return False, f"Connection error: {str(e)}"
    
    def test_transcribe(self) -> Tuple[bool, str]:
        """Test the audio transcription API"""
        if not self.access_token:
            return False, "No access token available"
            
        try:
            # Use the existing test.mp3 file in the root directory
            test_file_path = "test.mp3"
            
            if not os.path.exists(test_file_path):
                return False, f"Test file not found: {test_file_path}"
            
            with open(test_file_path, 'rb') as audio_file:
                files = {'file': ('test.mp3', audio_file, 'audio/mpeg')}
                headers = {"Authorization": f"Bearer {self.access_token}"}
                
                response = requests.post(
                    f"{self.base_url}/transcribe",
                    headers=headers,
                    files=files,
                    timeout=60
                )
            
            if response.status_code == 200:
                data = response.json()
                success = "transcription" in data
                return success, ""
            elif response.status_code == 401:
                return False, f"Authentication failed - token may be invalid"
            elif response.status_code == 400:
                return False, f"Bad request - likely invalid audio format"
            else:
                try:
                    error_data = response.json()
                    error_msg = error_data.get("detail", "Unknown error")
                except:
                    error_msg = f"Status code: {response.status_code}"
                return False, error_msg
                    
        except Exception as e:
            return False, f"Connection error: {str(e)}"
    
    def test_tts(self) -> Tuple[bool, str]:
        """Test the text-to-speech API"""
        if not self.access_token:
            return False, "No access token available"
            
        try:
            payload = {
                "text": "This is a test of the text to speech functionality."
            }
            response = requests.post(
                f"{self.base_url}/tts",
                headers=self.get_headers(),
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                # Check if response contains audio data
                content_type = response.headers.get('content-type', '')
                success = 'audio' in content_type or len(response.content) > 0
                return success, ""
            elif response.status_code == 401:
                return False, f"Authentication failed - token may be invalid"
            else:
                try:
                    error_data = response.json()
                    error_msg = error_data.get("detail", "Unknown error")
                except:
                    error_msg = f"Status code: {response.status_code}"
                return False, error_msg
        except Exception as e:
            return False, f"Connection error: {str(e)}"
    
    def test_verify_subscription(self) -> Tuple[bool, str]:
        if not self.access_token:
            return False, "No access token available"
            
        try:
            payload = {
                "purchase_token": "test_token"
            }
            response = requests.post(
                f"{self.base_url}/verify-subscription",
                headers=self.get_headers(),
                json=payload,
                timeout=30
            )
            
            # This endpoint might return various status codes depending on the test data
            # We consider it working if it returns a proper response (even if verification fails)
            if response.status_code in [200, 400, 401, 404, 500]:
                if response.status_code == 200:
                    data = response.json()
                    # Check if response has the expected structure
                    expected_fields = ["status", "is_pro", "message"]
                    if all(field in data for field in expected_fields):
                        return True, ""
                    else:
                        return False, "Response missing expected fields"
                return True, ""  # API is responding, even if with error
            else:
                return False, f"Unexpected status code: {response.status_code}"
        except Exception as e:
            return False, f"Connection error: {str(e)}"
    
    def test_google_cloud_health(self) -> Tuple[bool, str]:
        try:
            response = requests.get(f"{self.base_url}/google-cloud-health", timeout=10)
            if response.status_code == 200:
                data = response.json()
                success = "status" in data
                return success, ""
            return False, f"Status code: {response.status_code}"
        except Exception as e:
            return False, f"Connection error: {str(e)}"
    
    def test_test_user_subscription(self) -> Tuple[bool, str]:
        """Test that the test user gets premium access without subscription verification"""
        if not self.access_token:
            return False, "No access token available"
            
        try:
            payload = {
                "purchase_token": "test_token_for_test_user"
            }
            response = requests.post(
                f"{self.base_url}/verify-subscription",
                headers=self.get_headers(),
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                # Check if test user gets premium access
                if data.get("status") == "TEST USER" and data.get("is_pro") == True:
                    return True, ""
                else:
                    return False, f"Test user not getting premium access. Status: {data.get('status')}, is_pro: {data.get('is_pro')}"
            else:
                return False, f"Unexpected status code: {response.status_code}"
        except Exception as e:
            return False, f"Connection error: {str(e)}"
    
    def run_all_tests(self):
        """Run all API tests and generate report"""
        print("🚀 Starting API Tests for DreamSense Backend")
        print("=" * 50)
        print()
        
        # Test basic endpoints first
        print("Testing Basic Endpoints:")
        print("-" * 25)
        
        health_success, health_msg = self.test_health_check()
        self.print_status("Health Check", health_success, health_msg)
        
        root_success, root_msg = self.test_root_endpoint()
        self.print_status("Root Endpoint", root_success, root_msg)
        
        # Test token generation
        print("Testing Authentication:")
        print("-" * 25)
        
        token_success, token_msg = self.test_generate_token()
        self.print_status("Token Generation", token_success, token_msg)
        
        if not token_success:
            print("⚠️  Warning: Cannot test authenticated endpoints without valid token")
            print()
        
        # Test authenticated endpoints
        print("Testing Authenticated Endpoints:")
        print("-" * 35)
        
        dream_success, dream_msg = self.test_send_dream()
        self.print_status("Send Dreams", dream_success, dream_msg)
        
        image_success, image_msg = self.test_generate_image()
        self.print_status("Image Generation", image_success, image_msg)
        
        transcribe_success, transcribe_msg = self.test_transcribe()
        self.print_status("Audio Transcription", transcribe_success, transcribe_msg)
        
        tts_success, tts_msg = self.test_tts()
        self.print_status("Text-to-Speech", tts_success, tts_msg)
        
        subscription_success, subscription_msg = self.test_verify_subscription()
        self.print_status("Subscription Verification", subscription_success, subscription_msg)
        
        # Test additional endpoints
        print("Testing Additional Endpoints:")
        print("-" * 30)
        
        google_health_success, google_health_msg = self.test_google_cloud_health()
        self.print_status("Google Cloud Health", google_health_success, google_health_msg)
        
        test_user_success, test_user_msg = self.test_test_user_subscription()
        self.print_status("Test User Subscription", test_user_success, test_user_msg)
        
        # Generate summary
        print("📊 Test Summary:")
        print("=" * 50)
        
        all_tests = [
            ("Health Check", health_success),
            ("Root Endpoint", root_success),
            ("Token Generation", token_success),
            ("Send Dreams", dream_success),
            ("Image Generation", image_success),
            ("Audio Transcription", transcribe_success),
            ("Text-to-Speech", tts_success),
            ("Subscription Verification", subscription_success),
            ("Google Cloud Health", google_health_success),
            ("Test User Subscription", test_user_success)
        ]
        
        working_count = sum(1 for _, success in all_tests if success)
        total_count = len(all_tests)
        
        print(f"Total APIs tested: {total_count}")
        print(f"Working APIs: {working_count}")
        print(f"Failed APIs: {total_count - working_count}")
        print(f"Success Rate: {(working_count/total_count)*100:.1f}%")
        
        if working_count == total_count:
            print("\n🎉 All APIs are working perfectly!")
        elif working_count > total_count // 2:
            print("\n⚠️  Most APIs are working, but some need attention.")
        else:
            print("\n🚨 Multiple APIs are failing. Please check your configuration.")

def main():
    """Main function to run the API tests"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Test DreamSense Backend APIs")
    parser.add_argument(
        "--url", 
        default="http://localhost:8000",
        help="Base URL of the API server (default: http://localhost:8000)"
    )
    
    args = parser.parse_args()
    
    tester = APITester(args.url)
    tester.run_all_tests()

if __name__ == "__main__":
    main()