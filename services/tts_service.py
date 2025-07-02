from elevenlabs import ElevenLabs
from dotenv import load_dotenv
import os

load_dotenv()

client = ElevenLabs(
    api_key=os.getenv("ELEVENLABS_API_KEY"),
)

async def generate_tts_audio(text: str):
    """
    Generates TTS audio from the given text using ElevenLabs API.
    
    Args:
        text (str): The text to convert to speech
        
    Returns:
        bytes: Audio data in MP3 format
    """
    try:
        response = client.text_to_speech.convert(
            voice_id="co1DmUePVu3j1G6yCS55", 
            output_format="mp3_44100_128",
            text=text,
            model_id="eleven_multilingual_v2",
        )
        # Convert generator to bytes
        audio_bytes = b''.join(response)
        return audio_bytes
    except Exception as e:
        raise Exception(f"Failed to generate TTS audio: {str(e)}")
