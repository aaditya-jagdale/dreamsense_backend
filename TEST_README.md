# DreamSense API Test Script

This script tests all the APIs in your DreamSense backend and provides a comprehensive status report.

## Features

- ✅ Tests all major API endpoints
- 🚨 Provides clear status indicators (✅ for working, 🚨 for failing)
- 📊 Generates a summary report with success rates
- 🔐 Handles authentication automatically
- 🎯 Tests both basic and authenticated endpoints

## Prerequisites

1. Make sure your DreamSense backend server is running
2. Install the test dependencies:
   ```bash
   pip install -r test_requirements.txt
   ```

## Usage

### Basic Usage

```bash
python test_apis.py
```

### Custom Server URL

```bash
python test_apis.py --url http://your-server:8000
```

## What Gets Tested

### Basic Endpoints

- **Health Check** (`/health`) - Verifies server is running
- **Root Endpoint** (`/`) - Basic server response

### Authentication

- **Token Generation** (`/generate-token`) - Gets access token for authenticated endpoints

### Core APIs

- **Send Dreams** (`/send-dream`) - Tests dream processing functionality
- **Image Generation** (`/generate-image`) - Tests image generation with Gemini
- **Audio Transcription** (`/transcribe`) - Tests audio-to-text conversion
- **Text-to-Speech** (`/tts`) - Tests text-to-audio conversion
- **Subscription Verification** (`/verify-subscription`) - Tests Google Play subscription verification

### Additional Endpoints

- **Google Cloud Health** (`/google-cloud-health`) - Tests Google Cloud connectivity

## Sample Output

```
🚀 Starting API Tests for DreamSense Backend
==================================================

Testing Basic Endpoints:
-------------------------
✅ Health Check: Working

✅ Root Endpoint: Working

Testing Authentication:
-------------------------
✅ Token Generation: Working

Testing Authenticated Endpoints:
-----------------------------------
✅ Send Dreams: Working

✅ Image Generation: Working

🚨 Audio Transcription: Not working
   └─ Status code: 400

✅ Text-to-Speech: Working

✅ Subscription Verification: Working

Testing Additional Endpoints:
------------------------------
✅ Google Cloud Health: Working

📊 Test Summary:
==================================================
Total APIs tested: 9
Working APIs: 8
Failed APIs: 1
Success Rate: 88.9%

⚠️  Most APIs are working, but some need attention.
```

## Troubleshooting

### Common Issues

1. **Connection Refused**: Make sure your server is running on the specified URL
2. **Authentication Failed**: Check if your Supabase configuration is correct
3. **Timeout Errors**: Some APIs (like image generation) may take longer - the script uses appropriate timeouts
4. **Missing Dependencies**: Install requirements with `pip install -r test_requirements.txt`

### Environment Variables

Make sure your backend has all required environment variables set:

- `GEMINI_API_KEY`
- Supabase credentials
- Google Cloud credentials

## Notes

- The script creates temporary files for testing the transcription API
- All temporary files are automatically cleaned up
- The script uses realistic test data that should work with your APIs
- Timeouts are set appropriately for each endpoint type
