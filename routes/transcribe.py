from fastapi import APIRouter, File, UploadFile, Depends, HTTPException, Request
from google.genai import types
from google.genai import Client
import shutil

from routes.routes import verify_user_token

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
async def transcribe_endpoint(request: Request, file: UploadFile = File(...)):
    """
    API endpoint to transcribe an audio file.
    Requires a valid bearer token for authentication.
    """
    if not verify_user_token(request):
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    return await transcribe_audio(file)