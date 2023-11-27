from rest_framework import viewsets, status, permissions, generics
from .models import Post, Like, Comment
from .serializers import LikeSerializer, CommentSerializer, PostCreateSerializer, PostListSerializer, PostDetailSerializer
from .dalle import generate_image
from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from rest_framework.decorators import APIView, permission_classes
import requests
from django.core.files.base import ContentFile
import random
import urllib.request
from urllib.request import urlopen
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
        return Response({"image": str(image_url)})

class PostView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        print("request.user", request.user.id)
        user = request.user
        image_url = request.data["image_url"]
        print("image_url:", image_url)
        img_response = requests.get(image_url, stream=True)
        
        # author, image, title, content를 post_data라는 변수에 넣음
        post_data = {
            "author": user.id,
            "title": request.data["title"],
            "content": request.data["content"]
        }
        image_content = ContentFile(img_response.content, name="generated_image.png")
        post_data["generated_image"] = image_content

        # PostCreateSerializer에 post_data를 넣어 validation 후 저장
        post_serializer = PostCreateSerializer(data=post_data)
        if post_serializer.is_valid():
            # save 전, user가 동일한 이미지로 생성한 게 있는지 확인하고 있다면 status 400 띄우기
            post_serializer.save()
            return Response({"message": "Post가 성공적으로 생성됐습니다."})
        else:
            return Response({"error": post_serializer.errors}, status=400)

        
    def get(self, request, post_id=None):
        if post_id:
            # 상세보기
            user = request.user
            post = get_object_or_404(
                Post.objects.annotate(
                    likes_count=Count("likes", distinct=True),
                    comments_count=Count("comments", distinct=True),
                ),
                pk=post_id,
            )
            serializer = PostDetailSerializer(post)
            data = serializer.data
            if user.is_authenticated and post in user.likes.all():
                data["is_liked"] = True
            else:
                data["is_liked"] = False
            return Response(data, status=status.HTTP_200_OK)
        else:
            # 전체보기
            posts = (
                Post.objects.select_related("author")
                .only("author__nickname", "created_at")
                .order_by("-created_at")
            )

            serializer = PostListSerializer(posts, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)