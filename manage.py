#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys
'''
from django.core.management import execute_from_command_line
from posts.models import Post, GeneratedImage

def set_default_generated_image():
    # 이미 db에 저장된 이미지의 ID를 사용하여 가져오기
    default_generated_image_id = 1  # 여기에 이미지의 ID를 넣어주세요
    default_generated_image = GeneratedImage.objects.get(id=default_generated_image_id)

    # Post 모델 중에서 generated_image가 비어있는 경우 해당 이미지를 기본값으로 설정
    Post.objects.filter(generated_image__isnull=True).update(generated_image=default_generated_image)
'''

def main():
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'no_name.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
