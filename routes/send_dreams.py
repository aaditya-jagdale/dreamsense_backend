from agno.agent import Agent
from services.supabase import Supabase
from agno.models.google import Gemini
import os
from dotenv import load_dotenv

load_dotenv()

async def send_dream(query: str):
    supabase = Supabase()
    prompt = supabase.get_prompt()

    agent = Agent(
        name="Dreamer",
        description="A dreamer is a person who dreams about things",
        system_message=prompt,
        model=Gemini(api_key=os.getenv("GEMINI_API_KEY")),
    )

    response = agent.run(query).content
    return {
        "message": "Dream sent successfully",
        "success": True,
        "data": response,
    }