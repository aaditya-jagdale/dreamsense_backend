from supabase import create_client
from supabase.lib.client_options import SyncClientOptions
from routes.generate_images import generate_image
import io
import uuid
from PIL import Image
from utils.config import settings

class Supabase:
    def __init__(self):
        self.client = create_client(settings.supabase_url, settings.supabase_key)

    def get_user_id(self, token: str) -> str:
        response = self.client.auth.get_user(token)
        return response.user.id

    def verify_token(self, token: str) -> bool:
        try:
            print(f"Attempting to verify token with Supabase...")
            response = self.client.auth.get_user(token)
            print(f"Token verification successful for user: {response.user.id}")
            return True
        except Exception as e:
            print(f"Token verification failed with exception: {e}")
            return False

    def get_prompt(self):
        response = self.client.table("daily_read").select("contents").eq("title", "PROMPT").single().execute()
        return response.data.get("contents", "")

    def get_access_token(self):
        # subabase login via email
        response = self.client.auth.sign_in_with_password(credentials={"email": "test1@gmail.com", "password": "123456"})
        return response.session.access_token
    
    async def upload_image(self, prompt: str, access_token: str, user_profile: dict) -> str:
        # Get image prompt first
        image_prompt = self.get_image_prompt()
        
        # Generate the image using Gemini
        # Convert user_profile dict to string for the generate_image function
        user_profile_str = str(user_profile) if user_profile else ""
        img: Image.Image = await generate_image(prompt, user_profile_str, image_prompt)

        # Convert the image to bytes (PNG format)
        if(img is None):
            raise ValueError("Image generation failed")
        buffer = io.BytesIO()
        img.save(buffer, format="PNG")
        buffer.seek(0)

        # Unique filename for storage
        filename = f"{uuid.uuid4().hex}.png"
        bucket_name = "images"

        user_id = self.get_user_id(access_token)
        
        # Create path with user_id folder
        file_path = f"{user_id}/{filename}"
        storage_client = self.client
        try:
            storage_client = create_client(settings.supabase_url, settings.supabase_key, options= SyncClientOptions(
                headers={
                    "Authorization": f"Bearer {access_token}"
                }
            ))
        except Exception:
            # Fallback to default client if instantiation fails
            storage_client = self.client

        # Perform the upload using the (possibly) elevated client
        upload_response = storage_client.storage.from_(bucket_name).upload(
            path=file_path,
            file=buffer.getvalue(),
            file_options={
                "upsert": False,
                "content-type": "image/png",
            },
        )

        url_response = storage_client.storage.from_(bucket_name).create_signed_url(file_path, expires_in=60 * 60 * 24)

        # Extract the signed URL string from the response
        signed_url: str | None = None
        if isinstance(url_response, dict):
            # Supabase client may return keys "signedURL" or "signedUrl" depending on version
            signed_url = url_response.get("signedURL") or url_response.get("signedUrl")
        # Fallback to str representation if extraction failed
        if not signed_url:
            signed_url = str(url_response)

        return {"signed_url": signed_url, "filename": filename}
    
    def upload_dream(self, user_input: str, response: str, access_token: str) -> dict:
        user_id = self.get_user_id(access_token)
        supabase_res = create_client(settings.supabase_url, settings.supabase_key, options= SyncClientOptions(
            headers={
                "Authorization": f"Bearer {access_token}"
            }
        )).table("dreams").insert({
            "user_id": user_id,
            "description": user_input,
            "response": response,
        }).execute()
        return supabase_res.data[0]

    def get_user_profile(self, access_token: str) -> dict:
        user_id = self.get_user_id(access_token)
        response = self.client.table("users").select("questionare").eq("user_id", user_id).execute()
        if response.data and len(response.data) > 0:
            return response.data[0].get("questionare", {})
        return {}
    
    def get_user_dream_count(self, access_token: str) -> int:
        user_id = self.get_user_id(access_token)
        print("Dream count for user: ", user_id)
        response = create_client(settings.supabase_url, settings.supabase_key, options= SyncClientOptions(
            headers={
                "Authorization": f"Bearer {access_token}"
            }
        )).table("dreams").select("*").eq("user_id", user_id).execute()
        print("Dream count: ", len(response.data))
        return len(response.data) if response.data else 0
    
    def get_user_prev_dreams(self, access_token: str) -> int:
        user_id = self.get_user_id(access_token)
        print("Dream count for user: ", user_id)
        response = create_client(settings.supabase_url, settings.supabase_key, options= SyncClientOptions(
            headers={
                "Authorization": f"Bearer {access_token}"
            }
        )).table("dreams").select("description, created_at").eq("user_id", user_id).execute()
        return response.data
    def get_image_prompt(self) -> str:
        response = self.client.table("daily_read").select("contents").eq("title", "IMAGE").single().execute()
        return response.data.get("contents", "")


