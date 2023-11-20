from rest_framework import views, generics, status, permissions
from rest_framework.generics import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from django.contrib.auth import get_user_model, authenticate
#API 연결법
#from no_name.settings import DEEPL_API_KEY, KARLO_API_KEY
from .models import Post
#from . import constant
from posts.serializers import (
    PostListSerializer,
    PostDetailSerializer,
    PostCreateSerializer,
    CommentListSerializer,
    CommentCreateSerializer,
    ProductSerializer,
    ProductFrameSerializer,
    GeneratedImageSerializer,
)
#import deepl
import base64
from django.core.files.base import ContentFile
from django.core.files.uploadedfile import InMemoryUploadedFile
from datetime import datetime
from django.db.models import Count
from django.shortcuts import render
from .forms import ProductSizeForm, ProductFrameForm
from PIL import Image
from .dalle import generate_image
from .models import GeneratedImage
from django.core.serializers.json import DjangoJSONEncoder
#from .utils import generate_image  # 이곳에서 DALL-E 관련 함수를 import


class PostView(APIView):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    parser_classes = (MultiPartParser, FormParser)

    def get(self, request, post_id=None):
        if post_id:
            target = get_object_or_404(get_user_model(), pk=post_id)

            # 상세보기
            user = request.user
            post = get_object_or_404(
                Post.objects.annotate(
                    likes_count=Count("likes", distinct=True),
                    comments_count=Count("comments", distinct=True),
                ),
                pk=post_id,
            )
            serializer = PostDetailSerializer(post, context={'request': request})
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
                .annotate(
                    likes_count=Count("likes", distinct=True),
                    comments_count=Count("comments", distinct=True),
                )
                .order_by("-created_at")
            )

            serializer = PostListSerializer(posts, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

    def _process_image_data(self, data, key='image'):
        if key in data:
            image_data = data[key].read()
            encoded_image = base64.b64encode(image_data).decode('utf-8')
            decoded_image = base64.b64decode(encoded_image)
            image_name = data[key].name
            image_file = ContentFile(decoded_image, name=image_name)
            data[key] = image_file
            return True
        return False
    
    def post(self, request, *args, **kwargs):
        data = request.data

        # Ensure that a generated image is required
        if not self._process_image_data(data, key='generated_image'):
            return Response({"detail": "A generated image is required."}, status=status.HTTP_400_BAD_REQUEST)

        serializer = PostCreateSerializer(data=data)

        if serializer.is_valid():
            user = request.user
            serializer.save(author=user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
    def delete(self, request, post):
        post = get_object_or_404(Post, pk=post_id)
        user = request.user
        if post.author != user:
            return Response({"detail": "권한이 없습니다."}, status=status.HTTP_403_FORBIDDEN)
        post.delete()
        return Response({"detail": "삭제되었습니다"}, status=status.HTTP_200_OK)


class LikesView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, post_id):
        user = request.user
        post = get_object_or_404(Post, pk=post_id)
        author = post.author
        if user in post.likes.all():
            return Response(
                {"detail": "이미 좋아요를 눌렀습니다."}, status=status.HTTP_400_BAD_REQUEST
            )
        else:
            post.likes.add(user)
            author.save()
            author.refresh_from_db()
            History.objects.create(user=author, action="likes", point=author.point)
            return Response(
                {"likes_count": post.likes.count()}, status=status.HTTP_200_OK
            )


class CommentsView(APIView):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get(self, request, post_id):
        post = get_object_or_404(Post, pk=post_id)
        # 일반 댓글 가져옴
        comments = post.comments.select_related("author").only(
            "author__username", "content", "created_at"
        )
        comments_serializer = CommentListSerializer(comments, many=True)
        return Response(
            {"comments": comments_serializer.data}, status=status.HTTP_200_OK
        )

    def post(self, request, post_id):
        post = get_object_or_404(Post, pk=post_id)
        user = request.user
        if user == post.author:
            return Response({"detail": "권한이 없습니다"}, status=status.HTTP_403_FORBIDDEN)

        serializer = CommentCreateSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(author=user, post=post)
            return Response(
                {"data": serializer.data, "is_answer": False}, status=status.HTTP_200_OK
            )
        return Response({"detail": "유효하지 않은 댓글"}, status=status.HTTP_400_BAD_REQUEST)

        
class ProductView(APIView):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get(self, request, post_id):
        post = get_object_or_404(Post, pk=post_id)
        return Response(status=status.HTTP_200_OK)

    def choose_productsize(request):
        if request.method == 'POST':
            form = ProductSizeForm(request.POST)
            if form.is_valid():
                productsize_selected_choice = form.cleaned_data['size']
        else:
            form = ProductSizeForm()

        return render(request, 'my_template.html', {'form': form})

class ProductFrameView(APIView):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get(self, request, post_id):
        post = get_object_or_404(Post, pk=post_id)
        return Response(status=status.HTTP_200_OK)

    def choose_productframe(request):
        if request.method == 'POST':
            form = ProductFrameForm(request.POST)
            if form.is_valid():
                productframe_selected_choice = form.cleaned_data['frame']
        else:
            form = ProductFrameForm()

        return render(request, 'my_template.html', {'form': form})
    
class DalleAPIView(APIView):
    def post(self, request, *args, **kwargs):
        prompt = request.data.get('prompt')
        if not prompt:
            return Response({"error": "No prompt provided"}, status=400)

        image_url = generate_image(prompt)

        # 생성된 이미지 정보를 데이터베이스에 저장
        generated_image = GeneratedImage(prompt=prompt, image_url=image_url)
        generated_image.save()
        return Response({"image": str(image_url)})
