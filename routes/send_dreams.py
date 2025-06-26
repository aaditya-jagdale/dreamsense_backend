from agno.agent import Agent
from services.supabase import Supabase
from agno.models.google import Gemini
import os
from dotenv import load_dotenv
from pydantic import BaseModel, Field

load_dotenv()

class DreamOutput(BaseModel):
    message_output: str = Field(description="The message to send to the user")
    image_output: str = Field(description="An ultra detailed json context profile of the dream that would be used to generate an image")

async def send_dream(query: str):
    supabase = Supabase()
    prompt = supabase.get_prompt()

    agent = Agent(
        name="Dream Explainer",
        description="You are a dream explainer. You are given a dream and you need to explain it to the user in a way that is easy to understand. You need to use the image_output to generate an image of the dream.",
        system_message=prompt,
        response_model=DreamOutput,
        model=Gemini(id="gemini-2.5-flash", api_key=os.getenv("GEMINI_API_KEY")),
    )

    response = agent.run(query).content
    return {
        "message": "Dream sent successfully",
        "success": True,
        "data": response.message_output,
        "imageJsonProfile": response.image_output,
    }