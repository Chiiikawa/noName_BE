from openai import OpenAI
from django.conf import settings
from rest_framework.response import Response

client = OpenAI(api_key=settings.OPENAI_API_KEY)


def generate_image(prompt):
    
    response = client.images.generate(
    prompt=prompt,
    n=1,
    size="1024x1024")

    print(response.data[0].url)
    return Response({"image": response.data[0].url})