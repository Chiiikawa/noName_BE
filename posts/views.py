from rest_framework.generics import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
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
)
#import deepl
#import base64
from django.core.files.base import ContentFile
from datetime import datetime
from django.db.models import Count
from django.shortcuts import render
from .forms import ProductSizeForm


class PostView(APIView):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get(self, request, quiz_id=None):
        if post_id:
            # 상세보기
            user = request.user
            post = get_object_or_404(
                Quiz.objects.annotate(
                    likes_count=Count("likes", distinct=True),
                    comments_count=Count("comments", distinct=True),
                ),
                pk=quiz_id,
            )
            serializer = PostDetailSerializer(quiz)
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
                .only("author__username", "created_at", "solved")
                .annotate(
                    likes_count=Count("likes", distinct=True),
                    comments_count=Count("comments", distinct=True),
                )
                .order_by("-created_at")
            )

            serializer = PostListSerializer(posts, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        data = request.data
        encoded_image = data.get("image")
        decoded_image = base64.b64decode(encoded_image)
        current_time = int(datetime.now().timestamp())
        image_file = ContentFile(decoded_image, name=f"{current_time}.webp")
        data["image"] = image_file
        serializer = PostCreateSerializer(data=data)
        if serializer.is_valid():
            user = request.user
            serializer.save(author=user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, quiz_id):
        post = get_object_or_404(Post, pk=post_id)
        user = request.user
        if quiz.author != user:
            return Response({"detail": "권한이 없습니다."}, status=status.HTTP_403_FORBIDDEN)
        quiz.delete()
        return Response({"detail": "삭제되었습니다"}, status=status.HTTP_200_OK)


class LikesView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, quiz_id):
        user = request.user
        post = get_object_or_404(Post, pk=post_id)
        author = quiz.author
        if user in quiz.likes.all():
            return Response(
                {"detail": "이미 좋아요를 눌렀습니다."}, status=status.HTTP_400_BAD_REQUEST
            )
        else:
            quiz.likes.add(user)
            author.save()
            author.refresh_from_db()
            History.objects.create(user=author, action="likes", point=author.point)
            return Response(
                {"likes_count": quiz.likes.count()}, status=status.HTTP_200_OK
            )


class CommentsView(APIView):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get(self, request, quiz_id):
        post = get_object_or_404(Post, pk=post_id)
        # 일반 댓글 가져옴
        comments = post.comments.select_related("author").only(
            "author__username", "content", "created_at"
        )
        comments_serializer = CommentListSerializer(comments, many=True)
        return Response(
            {"comments": comments_serializer.data}, status=status.HTTP_200_OK
        )

    def post(self, request, quiz_id):
        quiz = get_object_or_404(Quiz, pk=quiz_id)
        user = request.user
        if user == quiz.author:
            return Response({"detail": "권한이 없습니다"}, status=status.HTTP_403_FORBIDDEN)

        serializer = CommentCreateSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(author=user, quiz=quiz)
            return Response(
                {"data": serializer.data, "is_answer": False}, status=status.HTTP_200_OK
            )
        return Response({"detail": "유효하지 않은 댓글"}, status=status.HTTP_400_BAD_REQUEST)


class ImageView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        user = request.user
        prompt = request.data.get("prompt")
        print(prompt)
        user.save()
        user.refresh_from_db()
        History.objects.create(user=user, action="create", point=user.point)
        #trnaslator와 Dall-E API 연결할부분
        #translator = deepl.Translator(DEEPL_API_KEY)
        #result = translator.translate_text(prompt, target_lang="EN-US")
        return Response(
            {"prompt": result.text, "API_KEY": KARLO_API_KEY}, status=status.HTTP_200_OK
        )
        
class ProductView(APIView):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get(self, request, post_id):
        post = get_object_or_404(Post, pk=post_id)
        # 일반 댓글 가져옴
        comments = post.comments.select_related("author").only(
            "author__username", "content", "created_at"
        )
        return Response(
            {"comments": comments_serializer.data}, status=status.HTTP_200_OK
        )

    def choose_productsize(request):
        if request.method == 'POST':
            form = ProductSizeForm(request.POST)
            if form.is_valid():
                selected_choice = form.cleaned_data['choice_field']
                # Do something with the selected choice
        else:
            form = ProductSizeForm()

        return render(request, 'my_template.html', {'form': form})

class ProductView(APIView):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get(self, request, post_id):
        post = get_object_or_404(Post, pk=post_id)
        # 일반 댓글 가져옴
        comments = post.comments.select_related("author").only(
            "author__username", "content", "created_at"
        )
        return Response(
            {"comments": comments_serializer.data}, status=status.HTTP_200_OK
        )

    def choose_productsize(request):
        if request.method == 'POST':
            form = ProductSizeForm(request.POST)
            if form.is_valid():
                selected_choice = form.cleaned_data['choice_field']
                # Do something with the selected choice
        else:
            form = ProductSizeForm()

        return render(request, 'my_template.html', {'form': form})