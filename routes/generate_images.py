from google.genai import types, Client
from PIL import Image
from io import BytesIO

async def generate_image(prompt: str, user_profile: str) -> Image.Image:
    client = Client()
    contents = ('Generate a very accurate image based on the given json profile.' + prompt + "Use this profile to make the image more customized" + user_profile)

    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash-preview-image-generation",
            contents=contents,
            config=types.GenerateContentConfig(
            response_modalities=['TEXT', 'IMAGE']
            )
        )

        # return a proper image in bytes
        for part in response.candidates[0].content.parts:
            if part.text is not None:
                print(part.text)
            elif part.inline_data is not None:
                return Image.open(BytesIO(part.inline_data.data))
    except Exception as e:
        print(e)
        return None
