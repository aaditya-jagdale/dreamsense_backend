from fastapi import APIRouter, File, UploadFile, Depends, HTTPException, Request
from google.genai import types
from google.genai import Client
import shutil
from services.tts_service import generate_tts_audio
from fastapi.responses import Response
from pydantic import BaseModel
import os
import json
from utils.auth import auth_service
from schemas.requests import TTSRequest
from schemas.responses import TTSResponse

router = APIRouter()
client = Client()

def is_valid_audio_file(audio_file: UploadFile) -> bool:
    """
    Validates if the uploaded file is a valid audio file.
    Supports multiple audio formats that Google Gemini can process.
    """
    # Google Gemini supported audio formats
    valid_content_types = [
        # MP3 formats
        "audio/mpeg",
        "audio/mp3", 
        "audio/mpeg3",
        "audio/x-mpeg-3",
        "audio/x-mp3",
        # WAV formats
        "audio/wav",
        "audio/x-wav",
        "audio/wave",
        # M4A formats
        "audio/mp4",
        "audio/x-m4a",
        "audio/aac",
        # OGG formats
        "audio/ogg",
        "audio/oga",
        # FLAC format
        "audio/flac",
        "audio/x-flac",
        # WebM format
        "audio/webm",
        # General audio
        "audio/*"
    ]
    
    # Check content type
    if audio_file.content_type in valid_content_types:
        return True
    
    # Check file extension as fallback
    if audio_file.filename:
        file_extension = os.path.splitext(audio_file.filename)[1].lower()
        supported_extensions = [
            '.mp3', '.mpeg', '.mpeg3',
            '.wav', '.wave',
            '.m4a', '.aac',
            '.ogg', '.oga',
            '.flac',
            '.webm'
        ]
        if file_extension in supported_extensions:
            return True
    
    return False

def normalize_mime_type(content_type: str, filename: str = None) -> str:
    """
    Normalizes MIME type to ensure compatibility with Google Gemini.
    Falls back to file extension if content type is not recognized.
    """
    # Direct mapping for common content types
    mime_type_mapping = {
        "audio/mpeg": "audio/mpeg",
        "audio/mp3": "audio/mpeg",
        "audio/mpeg3": "audio/mpeg",
        "audio/x-mpeg-3": "audio/mpeg",
        "audio/x-mp3": "audio/mpeg",
        "audio/wav": "audio/wav",
        "audio/x-wav": "audio/wav",
        "audio/wave": "audio/wav",
        "audio/mp4": "audio/mp4",
        "audio/x-m4a": "audio/mp4",
        "audio/aac": "audio/mp4",
        "audio/ogg": "audio/ogg",
        "audio/oga": "audio/ogg",
        "audio/flac": "audio/flac",
        "audio/x-flac": "audio/flac",
        "audio/webm": "audio/webm"
    }
    
    # Try to normalize the content type
    if content_type in mime_type_mapping:
        return mime_type_mapping[content_type]
    
    # Fallback to file extension if content type is not recognized
    if filename:
        file_extension = os.path.splitext(filename)[1].lower()
        extension_mapping = {
            '.mp3': 'audio/mpeg',
            '.mpeg': 'audio/mpeg',
            '.mpeg3': 'audio/mpeg',
            '.wav': 'audio/wav',
            '.wave': 'audio/wav',
            '.m4a': 'audio/mp4',
            '.aac': 'audio/mp4',
            '.ogg': 'audio/ogg',
            '.oga': 'audio/ogg',
            '.flac': 'audio/flac',
            '.webm': 'audio/webm'
        }
        if file_extension in extension_mapping:
            return extension_mapping[file_extension]
    
    # Default fallback
    return "audio/mpeg"

async def transcribe_audio(audio_file: UploadFile):
    """
    Transcribes the given audio file using Google's Gemini model.
    """
    if not audio_file:
        raise HTTPException(status_code=400, detail="No audio file provided.")

    if not is_valid_audio_file(audio_file):
        raise HTTPException(
            status_code=400, 
            detail="Invalid audio file type. Supported formats: MP3, WAV, M4A, AAC, OGG, FLAC, WebM. Please ensure your file has a supported extension or correct audio content type."
        )

    try:
        # Read audio data
        audio_bytes = await audio_file.read()
        
        # Normalize MIME type for Gemini
        normalized_mime_type = normalize_mime_type(audio_file.content_type, audio_file.filename)

        # Generate transcription
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=[
                'Generate a super precise and detailed transcription of the following audio clip. Do not include any other text or commentary. But you dont have to transcribe the entire audio clip. Just summarize the most important parts.',
                types.Part.from_bytes(
                    data=audio_bytes,
                    mime_type=normalized_mime_type,
                )
            ]
        )
        return {"transcription": response.text}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to transcribe audio: {str(e)}")

@router.post("/transcribe")
async def transcribe_endpoint(file: UploadFile = File(...), auth_token: str = Depends(auth_service.require_auth)):
    """
    API endpoint to transcribe an audio file.
    Requires a valid bearer token for authentication.
    """
    return await transcribe_audio(file)

@router.post("/tts", response_model=TTSResponse)
async def tts_endpoint(request: TTSRequest, auth_token: str = Depends(auth_service.require_auth)):
    response = await generate_tts_audio(request.text)
    return response