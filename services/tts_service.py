import httpx
import json
from utils.config import settings

async def generate_tts_audio(text: str):
    url = "https://api.v8.unrealspeech.com/speech"
    headers = {
        "Authorization": f"Bearer {settings.unrealspeech_api_key}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "Text": text,
        "VoiceId": "Sierra",
        "Bitrate": "320k",
        "AudioFormat": "mp3",
        "OutputFormat": "uri",
        "TimestampType": "sentence",
        "sync": False
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.post(url, headers=headers, json=payload)
        return response.json()
