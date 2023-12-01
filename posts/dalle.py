from openai import OpenAI
from django.conf import settings
from rest_framework.response import Response
from django.http import HttpResponseForbidden
from django.core.cache import cache

client = OpenAI(api_key=settings.OPENAI_API_KEY)

class DALLERateLimitMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # OpenAI API 호출 횟수 제한을 위한 캐시 키
        openai_call_key = 'openai_call_count'

        # 캐시에서 현재 OpenAI API 호출 횟수 가져오기
        openai_call_count = cache.get(openai_call_key, 0)

        # 설정된 허용된 OpenAI API 호출 횟수 (예: 1000회)
        allowed_openai_calls = 1000

        # 현재 OpenAI API 호출 횟수 증가
        openai_call_count += 1

        # 캐시 업데이트
        cache.set(openai_call_key, openai_call_count)

        # 현재 OpenAI API 호출 횟수가 허용된 호출 횟수를 초과하면 요청 거부
        if openai_call_count > allowed_openai_calls:
            return HttpResponseForbidden("OpenAI API 호출 횟수가 초과되었습니다.")

        response = self.get_response(request)
        return response

def generate_image(prompt):
    response = client.images.generate(
        prompt=prompt,
        n=1,
        size="1024x1024"
    )
    print(response.data[0].url)
    return response.data[0].url