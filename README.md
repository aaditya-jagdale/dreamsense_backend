# DreamSense API

A FastAPI-based REST API for AI-powered dream analysis and interpretation with subscription management and image generation capabilities.

## 🚀 Features

- **Dream Analysis**: AI-powered dream interpretation using Gemini
- **Image Generation**: Generate visual representations of dreams
- **Audio Transcription**: Convert voice recordings to text
- **Text-to-Speech**: Convert text responses to audio
- **Subscription Management**: Google Play subscription verification
- **User Management**: Supabase-based user authentication and profiles
- **Free Trial System**: Limited free access with upgrade options

## 📁 Project Structure

```
dreamsense/
├── app.py                          # Main FastAPI application
├── requirements.txt                # Python dependencies
├── Dockerfile                      # Docker configuration
├── utils/                          # Reusable utilities
│   ├── __init__.py
│   ├── auth.py                     # Authentication utilities
│   ├── validators.py               # Request validation utilities
│   ├── error_handler.py            # Error handling utilities
│   └── config.py                   # Configuration management
├── schemas/                        # Pydantic models
│   ├── __init__.py
│   ├── requests.py                 # Request schemas
│   └── responses.py                # Response schemas
├── services/                       # Business logic services
│   ├── supabase.py                 # Supabase database operations
│   ├── google_cloud_utils.py       # Google Cloud utilities
│   ├── google_cloud.py             # Google Cloud integration
│   ├── purchase_verification.py    # Purchase verification
│   ├── subscription_service.py     # Subscription management
│   └── tts_service.py              # Text-to-speech service
└── routes/                         # API route handlers
    ├── routes.py                   # Main API routes
    ├── transcribe.py               # Audio transcription routes
    ├── send_dreams.py              # Dream analysis logic
    └── generate_images.py          # Image generation logic
```

## 🛠️ Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd dreamsense
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**
   Create a `.env` file with the following variables:
   ```env
   # Supabase Configuration
   SUPABASE_URL=your_supabase_url
   SUPABASE_KEY=your_supabase_key
   
   # Google Cloud Configuration
   GOOGLE_SERVICE_ACCOUNT_JSON_B64=your_base64_encoded_service_account_json
   
   # API Keys
   GEMINI_API_KEY=your_gemini_api_key
   ELEVENLABS_API_KEY=your_elevenlabs_api_key
   
   # App Configuration
   APP_NAME=DreamSense API
   APP_VERSION=1.0.0
   DEBUG=false
   
   # Subscription Configuration
   PACKAGE_NAME=com.dreamsense.app
   SUBSCRIPTION_ID=dreamsense_pro_1
   FREE_TRIAL_DREAMS=2
   ```

4. **Run the application**
   ```bash
   uvicorn app:app --reload
   ```

## 📚 API Documentation

The API documentation is automatically generated and available at:
- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

### Base URL
All endpoints are prefixed with `/api/v1`

### Authentication
Most endpoints require authentication via Bearer token in the Authorization header:
```
Authorization: Bearer <your_access_token>
```

## 🔌 API Endpoints

### Health & Status
- `GET /api/v1/health` - Health check endpoint
- `GET /api/v1/` - Root endpoint
- `GET /api/v1/google-cloud-health` - Google Cloud credentials health check

### Authentication
- `GET /api/v1/generate-token` - Generate test access token

### Dream Analysis
- `POST /api/v1/send-dream` - Analyze and interpret a dream
  ```json
  {
    "query": "I was flying over a city",
    "purchase_token": "com.dreamsense.app.subscription"
  }
  ```

### Image Generation
- `POST /api/v1/generate-image` - Generate an image from a prompt
  ```json
  {
    "prompt": "A detailed image of a flying person over a city"
  }
  ```

### Subscription Management
- `POST /api/v1/verify-subscription` - Verify user subscription status
  ```json
  {
    "purchase_token": "your_purchase_token"
  }
  ```

### Audio Processing
- `POST /api/v1/transcribe` - Transcribe audio file (multipart/form-data)
- `POST /api/v1/tts` - Convert text to speech
  ```json
  {
    "text": "Your dream interpretation text"
  }
  ```

## 🔧 Key Improvements Made

### 1. **Request/Response Validation**
- Added Pydantic models for all request and response schemas
- Automatic validation of request payloads
- Consistent response formats across all endpoints

### 2. **Authentication Centralization**
- Created `AuthService` for centralized token verification
- Dependency injection for authentication requirements
- Consistent error handling for authentication failures

### 3. **Code Reusability**
- Extracted common utilities into reusable components
- Consolidated Google Cloud services to eliminate duplication
- Created centralized configuration management

### 4. **Error Handling**
- Consistent error response formats
- Centralized error handling utilities
- Proper HTTP status codes for different error types

### 5. **Configuration Management**
- Type-safe configuration using Pydantic Settings
- Environment variable validation
- Centralized configuration access

### 6. **API Structure**
- Organized endpoints with proper prefixes and tags
- Clear separation of concerns
- Improved API documentation

## 🧪 Testing

Run the test suite:
```bash
pytest test_apis.py
```

## 🐳 Docker Deployment

Build and run with Docker:
```bash
docker build -t dreamsense-api .
docker run -p 8000:8000 dreamsense-api
```

## 📝 Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `SUPABASE_URL` | Supabase project URL | Yes |
| `SUPABASE_KEY` | Supabase service key | Yes |
| `GOOGLE_SERVICE_ACCOUNT_JSON_B64` | Base64 encoded Google service account JSON | Yes |
| `GEMINI_API_KEY` | Google Gemini API key | Yes |
| `ELEVENLABS_API_KEY` | ElevenLabs API key | Yes |
| `PACKAGE_NAME` | Android app package name | No (default: com.dreamsense.app) |
| `SUBSCRIPTION_ID` | Google Play subscription ID | No (default: dreamsense_pro_1) |
| `FREE_TRIAL_DREAMS` | Number of free trial dreams | No (default: 2) |

## 🔒 Security Features

- Bearer token authentication
- Request payload validation
- Environment variable protection
- Error message sanitization
- Subscription verification

## 📊 Response Formats

All API responses follow a consistent format:

### Success Response
```json
{
  "success": true,
  "message": "Operation completed successfully",
  "data": {...}
}
```

### Error Response
```json
{
  "success": false,
  "message": "Error description",
  "type": "error_type",
  "details": {...}
}
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License. 