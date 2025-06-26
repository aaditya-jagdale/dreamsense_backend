from supabase import create_client
from supabase.lib.client_options import SyncClientOptions
from dotenv import load_dotenv
import os
from routes.generate_images import generate_image
import io
import uuid
from PIL import Image

load_dotenv()

class Supabase:
    def __init__(self):
        self.client = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))

    def get_user_id(self, token: str) -> str:
        response = self.client.auth.get_user(token)
        return response.user.id

    def verify_token(self, token: str) -> bool:
        try:
            self.client.auth.get_user(token)
            return True
        except Exception:
            return False

    def get_prompt(self):
        response = self.client.table("daily_read").select("*").eq("title", "PROMPT").execute()

    def get_access_token(self):
        # subabase login via email
        response = self.client.auth.sign_in_with_password(credentials={"email": "aadi@gmail.com", "password": "123456"})
        return response.session.access_token
    
    async def upload_image(self, prompt: str, access_token: str) -> str:
        # Generate the image using Gemini
        img: Image.Image = await generate_image(prompt)

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
            storage_client = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"), options= SyncClientOptions(
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

        url_response = storage_client.storage.from_(bucket_name).create_signed_url(file_path, expires_in=60 * 60 * 1)

        # Extract the signed URL string from the response
        signed_url: str | None = None
        if isinstance(url_response, dict):
            # Supabase client may return keys "signedURL" or "signedUrl" depending on version
            signed_url = url_response.get("signedURL") or url_response.get("signedUrl")
        # Fallback to str representation if extraction failed
        if not signed_url:
            signed_url = str(url_response)

        return signed_url