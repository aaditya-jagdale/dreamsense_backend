from agno.agent import Agent
from services.supabase_client import Supabase
from agno.models.google import Gemini
from pydantic import BaseModel, Field
from utils.config import settings


supabase = Supabase()

class DreamOutput(BaseModel):
    message_output: str = Field(description="The message to send to the user")
    image_output: str = Field(description="An ultra detailed json context profile of the dream that would be used to generate an image")

async def send_dream(query: str, access_token: str, user_profile: str):
    try:
        # Initialize Supabase and get required data
        prompt = supabase.get_prompt()
        if not prompt:
            raise ValueError("Failed to retrieve prompt from database")
            
        prev_dreams = supabase.get_user_prev_dreams(access_token=access_token)

        # Validate API key
        api_key = settings.gemini_api_key
        if not api_key:
            raise ValueError("Missing Gemini API key")

        # Initialize and run agent
        agent = Agent(
            name="Dream Explainer",
            description="You are a dream explainer. You are given a dream and you need to explain it to the user in a way that is easy to understand. You need to use the image_output to generate an image of the dream.",
            system_message=prompt,
            context=user_profile,
            additional_context=prev_dreams,
            add_context=True,
            response_model=DreamOutput,
            model=Gemini(id="gemini-2.5-flash", api_key=api_key),
        )

        response = agent.run(query)
        if not response or not response.content:
            raise ValueError("Failed to generate response from agent")

        # Validate response fields
        if not response.content.message_output or not response.content.image_output:
            raise ValueError("Invalid response format from agent")

        return {
            "message": "Dream sent successfully",
            "success": True,
            "data": response.content.message_output,       
        }

    except ValueError as e:
        return {
            "message": str(e),
            "success": False,
            "data": None
        }
    except Exception as e:
        return {
            "message": f"An unexpected error occurred: {str(e)}",
            "success": False,
            "data": None
        }