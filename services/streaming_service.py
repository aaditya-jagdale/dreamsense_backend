import os
import asyncio
from typing import AsyncGenerator
from google.genai import Client
from services.supabase_client import Supabase
from utils.config import settings

supabase = Supabase()

class StreamingService:
    def __init__(self):
        self.client = Client(api_key=settings.gemini_api_key)
        self.model = "gemini-2.5-flash"
    
    async def stream_dream_analysis(self, query: str, access_token: str, user_profile: str) -> AsyncGenerator[str, None]:
        try:
            prompt = supabase.get_prompt()
            if not prompt:
                yield "Error: Failed to retrieve prompt from database"
                return

            prev_dreams = supabase.get_user_prev_dreams(access_token=access_token)
            full_prompt = self._build_prompt(prompt, query, user_profile, prev_dreams)

            stream = self.client.models.generate_content_stream(
                model=self.model,
                contents=[{"parts": [{"text": full_prompt}]}],
                config={
                    "temperature": 0.7,
                    "top_p": 0.8,
                    "top_k": 40,
                    "max_output_tokens": 2048,
                }
            )

            # Convert synchronous generator to async generator
            async def async_stream():
                for response in stream:
                    yield response
            
            async for response in async_stream():
                for candidate in response.candidates:
                    for part in candidate.content.parts:
                        text = part.text
                        if text:
                            yield text

        except Exception as e:
            yield f"Error in streaming: {str(e)}"
    
    def _build_prompt(self, system_prompt: str, query: str, user_profile: str, prev_dreams: str) -> str:
        """
        Build the complete prompt with system message, user profile, previous dreams, and current query.
        
        Args:
            system_prompt: The base system prompt
            query: Current dream query
            user_profile: User's profile information
            prev_dreams: User's previous dreams for context
            
        Returns:
            str: Complete formatted prompt
        """
        prompt_parts = []
        
        # Add system prompt
        prompt_parts.append(f"System: {system_prompt}")
        
        # Add user profile if available
        if user_profile and user_profile.strip():
            prompt_parts.append(f"User Profile: {user_profile}")
        
        # Add previous dreams context if available
        if prev_dreams and prev_dreams.strip():
            prompt_parts.append(f"Previous Dreams Context: {prev_dreams}")
        
        # Add current dream query
        prompt_parts.append(f"Current Dream: {query}")
        
        # Add instruction for response
        prompt_parts.append("Please provide a detailed analysis of this dream, explaining its meaning and symbolism in a clear, accessible way.")
        
        return "\n\n".join(prompt_parts)

# Create a singleton instance
streaming_service = StreamingService() 