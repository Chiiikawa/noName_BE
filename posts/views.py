from rest_framework import viewsets, status, permissions, generics
from .models import Post, Like, Comment, GeneratedImage
from .serializers import LikeSerializer, CommentSerializer, PostCreateSerializer
from .dalle import generate_image
from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from rest_framework.decorators import APIView, permission_classes
import requests
from django.core.files.base import ContentFile

class LikeViewSet(viewsets.ModelViewSet):
    queryset = Like.objects.all()
    serializer_class = LikeSerializer
    
class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    
class DalleAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    def post(self, request, *args, **kwargs):
        prompt = request.data.get('prompt') # 클라이언트 요청에서 prompt라는 데이터를 가져옴, prompt는 사용자가 입력한 텍스트 prompt, 이미지 생성에 사용함.
        if not prompt:  # prompt가 비어있거나 없는 경우를 확인함.
            return Response({"error": "No prompt provided"}, status=400)

        image_url = generate_image(prompt)  # generate_image 함수를 호출하여 입력된 prompt를 바탕으로 이미지를 생성하고, 생성된 이미지 URL을 image_url 변수에 저장.
        print("image_url은 다음과 같습니다.:", image_url)
        # 생성된 이미지 정보를 데이터베이스에 저장
        generated_image = GeneratedImage(prompt=prompt, image_url=image_url, author=request.user)    # GeneratedImage 모델 인스턴스를 생성함, 생성된 이미지의 prompt와 url을 저장함.
        generated_image.save()
        return Response({"image": str(image_url)})

class PostView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    # def download_and_save_image(image_url):
    #     response = requests.get(image_url)
    #     if response.status_code == 200:
    #         image_name = image_url.split('/')[-1]
    #         image_model = Post()
    #         image_model.generated_image.save(image_name, ContentFile(response.content), save=True)
    def post(self, request):
        print("request.user", request.user.id)
        user = request.user
        latest_generated_image = GeneratedImage.objects.filter(author=user).last()

        # 이 부분에서 필요한 작업을 수행하고, 예를 들어 포스트 작성 등을 진행할 수 있습니다.
        # 예시로, latest_generated_image를 사용하여 포스트를 작성하는 코드를 추가했습니다.
        print("author:", user.id)
        print("generated_image:", latest_generated_image)
        print("title:", request.data["title"])
        print("content:", request.data["content"])
        post_data = {
            "author": user.id,
            "generated_image": latest_generated_image.id,
            "title": request.data["title"],
            "content": request.data["content"]
        }

        post_serializer = PostCreateSerializer(data=post_data)
        if post_serializer.is_valid():
            # save 전, user가 동일한 이미지로 생성한 게 있는지 확인하고 있다면 status 400 띄우기
            post_serializer.save()
            return Response({"message": "Post가 성공적으로 생성됐습니다."})
        else:
            return Response({"error": post_serializer.errors}, status=400)

# 유저가 마지막으로 생성한 Generated image의 url을 프론트에 보내는 View. 프론트는 이 url을 img tag에 넣어 이미지를 띄운다. 
# 프론트에서 상태관리를 잘 사용하면 Generatedimage라는 모델과 이 View 없이도 url을 받을 수 있을듯.
class GetGeneratedImageView(APIView):
    def get(self, request):
        user = request.user
        latest_generated_image = GeneratedImage.objects.filter(author=user).last()
        print("author:", user.id)
        if (latest_generated_image):
            print("generated_image:", latest_generated_image)
            print("프롬프트:", latest_generated_image.prompt)
            print(latest_generated_image.image_url)
            return Response({"image_url": latest_generated_image.image_url})
        else:
            return Response({"error": post_serializer.errors}, status=400)
