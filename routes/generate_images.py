from google import genai
from google.genai import types
from PIL import Image
from io import BytesIO

# client = genai.Client()

def generate_image(prompt: str) -> Image.Image:
    client = genai.Client()

    contents = ('Generate a 3d rendered image of my dream. Dont limit this to be realistic. Make it as creative as possible. The image should be generate from my POV. I should me the main character. No matter if I am the good guy or the bad guy. If my dream is a nightmare, make it as scary as possible. ' + prompt)

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
    
# for part in response.candidates[0].content.parts:
#   if part.text is not None:
#     print(part.text)
#   elif part.inline_data is not None:
#     image = Image.open(BytesIO((part.inline_data.data)))
#     image.save('gemini-native-image.png')
#     image.show()