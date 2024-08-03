from io import BytesIO

import requests
from django.conf import settings
from openai import OpenAI

OPENAPI_DALL_E_3_SIZES = {"256x256", "512x512", "1024x1024", "1792x1024", "1024x1792"}


def generate_ai_image(prompt: str, size: str) -> BytesIO:
    client = OpenAI(api_key=settings.OPENAI_API_KEY)
    if size not in OPENAPI_DALL_E_3_SIZES:
        raise ValueError(f"Invalid size: {size}")

    prompt = prompt + "\n\n위 내용은 프로젝트를 같이할 사람을 모집하기 위한 내용입니다.\n\n내용을 기반으로 자연스러운 메인 이미지를 생성해주세요.\n\n이미지에는 글자가 들어가면 안됩니다."
    response = client.images.generate(
        model="dall-e-3",
        prompt=prompt,
        n=1,
        size=size,
        quality="standard",
    )
    try:
        image_url = response.data[0].url
    except (IndexError, AttributeError) as e:
        raise ValueError(f"Image URL Error: {e}")
    image_response = requests.get(image_url)

    # Ensure the request was successful
    if image_response.status_code == 200:
        # Open the image and save it to a file
        return BytesIO(image_response.content)
    raise ValueError("Image Response Error")
