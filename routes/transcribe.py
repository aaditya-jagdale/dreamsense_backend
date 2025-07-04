from fastapi import APIRouter, File, UploadFile, Depends, HTTPException, Request
from google.genai import types
from google.genai import Client
import shutil
from services.tts_service import generate_tts_audio
from fastapi.responses import Response
from pydantic import BaseModel

from utils.auth import auth_service
from schemas.requests import TTSRequest

router = APIRouter()
client = Client()

async def transcribe_audio(audio_file: UploadFile):
    """
    Transcribes the given audio file using Google's Gemini model.
    """
    if not audio_file:
        raise HTTPException(status_code=400, detail="No audio file provided.")

    if audio_file.content_type not in ["audio/mpeg", "audio/mp3"]:
        raise HTTPException(status_code=400, detail="Invalid audio file type. Only MP3 is supported.")

    try:
        # Read audio data
        audio_bytes = await audio_file.read()

        # Generate transcription
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=[
                'Generate a super precise and detailed transcription of the following audio clip. Do not include any other text or commentary. But you dont have to transcribe the entire audio clip. Just summarize the most important parts.',
                types.Part.from_bytes(
                    data=audio_bytes,
                    mime_type=audio_file.content_type,
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

@router.post("/tts")
async def tts_endpoint(request: TTSRequest, auth_token: str = Depends(auth_service.require_auth)):
    try:
        audio_bytes = await generate_tts_audio(request.text)
        return Response(
            content=audio_bytes,
            media_type="audio/mpeg",
            headers={"Content-Disposition": "attachment; filename=tts_audio.mp3"}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate TTS audio: {str(e)}")    