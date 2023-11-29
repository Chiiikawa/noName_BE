from rest_framework import viewsets, status, permissions, generics
from .models import Post, Like, Comment
from .serializers import LikeSerializer, CommentSerializer, CommentCreateSerializer, PostCreateSerializer, PostListSerializer, PostDetailSerializer
from .dalle import generate_image
from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from rest_framework.decorators import APIView, permission_classes, action
import requests
import random
import urllib.request
from urllib.request import urlopen
from django.core.files.base import ContentFile
from datetime import datetime
from django.db.models import Count
from . import constant
from django.db.models import F
from accounts.models import History

class LikeView(APIView):
    queryset = Like.objects.all()
    serializer_class = LikeSerializer

    def post(self, request):
        # request.user는 현재 로그인한 사용자를 나타냅니다.
        user = request.user
        post_id = request.data.get("post_id")
        post = get_object_or_404(Post, pk=post_id)
        author = post.author

        existing_like = Like.objects.filter(user=user, post=post).first()
        if existing_like:
            existing_like.delete()

            return Response(
                {"likes_count": post.likes.count(), "is_liked": False},
                status=status.HTTP_200_OK
            )
        else:
            # 좋아요 추가
            Like.objects.create(user=user, post=post)

            return Response(
                {"likes_count": post.likes.count(), "is_liked": True}, status=status.HTTP_200_OK
            )

class CommentView(APIView):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer

    def post(self, request):
        post_id = request.data.get('post_id')
        post = get_object_or_404(Post, pk=post_id)
        user = request.user

        serializer = CommentCreateSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=user, post=post)
            return Response(
                {"data": serializer.data,}, status=status.HTTP_200_OK
            )
        else:
            #에러 메시지 출력
            return Response({"detail": "유효하지 않은 댓글","errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
    
class DalleAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    def post(self, request, *args, **kwargs):
        prompt = request.data.get('prompt') # 클라이언트 요청에서 prompt라는 데이터를 가져옴, prompt는 사용자가 입력한 텍스트 prompt, 이미지 생성에 사용함.
        user = request.user
        if user.point < constant.API_REQUEST_POINT:
            return Response({"detail": "포인트가 부족합니다."}, status=status.HTTP_403_FORBIDDEN)
        user.point = F("point") - constant.API_REQUEST_POINT
        user.save()
        user.refresh_from_db()
        History.objects.create(user=user, action="create", point=user.point)
        if not prompt:  # prompt가 비어있거나 없는 경우를 확인함.
            return Response({"error": "No prompt provided"}, status=400)

        image_url = generate_image(prompt)  # generate_image 함수를 호출하여 입력된 prompt를 바탕으로 이미지를 생성하고, 생성된 이미지 URL을 image_url 변수에 저장.
        return Response({"image": str(image_url)})

class PostView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    def get(self, request, post_id=None):
        if post_id: #post_id가 존재하면 특정 게시물의 상세 정보를 요청함.
            # 상세보기
            user = request.user #현재 요청을 보낸 사용자를 가져옴.
            post = get_object_or_404(
                Post.objects.annotate(
                    likes_count=Count("likes", distinct=True),
                    comments_count=Count("comments", distinct=True),
                ),
                pk=post_id,
            )

            # LikeViewSet을 사용하여 좋아요 정보 가져오기
            like_queryset = Like.objects.filter(post=post)
            like_serializer = LikeSerializer(like_queryset, many=True) #가져온 정보를 직렬화

            # CommentViewSet을 사용하여 댓글 정보 가져오기
            comment_queryset = Comment.objects.filter(post=post)
            comment_serializer = CommentSerializer(comment_queryset, many=True)

            serializer = PostDetailSerializer(post) #현재 게시물에 대한 상세 정보를 직렬화
            data = serializer.data #직렬화된 데이터를 data 변수에 저장
            data["likes"] = like_serializer.data #딕셔너리에 각각 좋아요와 댓글 정보를 추가
            data["comments"] = comment_serializer.data

            if user.is_authenticated and post in user.likes.all(): #현재 사용자가 로그인되어 있고, 이 사용자가 현재 조회 중인 게시물을 좋아요한 경우
                data["is_liked"] = True #data 딕셔너리에 "is_liked" 키를 추가하고 값을 True로 설정
            else: #만약 사용자가 로그인되어 있지 않거나 현재 조회 중인 게시물을 좋아요하지 않은 경우, data 딕셔너리에 "is_liked" 키를 추가하고 값을 False로 설정
                data["is_liked"] = False

            return Response(data, status=status.HTTP_200_OK) #직렬화된 데이터와 함께 HTTP 200 OK 상태 코드를 갖는 응답을 반환
        else:
            # 전체보기
            posts = (
                Post.objects.all() #모든 게시물을 가져오는데, select_related를 사용하여 게시물의 작성자 정보를 미리 가져옴
                .order_by("-created_at") #order_by로 게시물을 최신순으로 정렬
            )

            serializer = PostListSerializer(posts, many=True) #가져온 게시물들을 PostListSerializer를 사용하여 직렬화
            return Response(serializer.data, status=status.HTTP_200_OK) #직렬화된 데이터와 함께 HTTP 200 OK 상태 코드를 갖는 응답을 반환합니다. 이는 전체 게시물 목록을 나타냄

    def post(self, request):
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
        current_time = int(datetime.now().timestamp())
        image_content = ContentFile(img_response.content, name=f"{current_time}.png")
        post_data["generated_image"] = image_content

        # PostCreateSerializer에 post_data를 넣어 validation 후 저장
        post_serializer = PostCreateSerializer(data=post_data)
        if post_serializer.is_valid():
            # save 전, user가 동일한 이미지로 생성한 게 있는지 확인하고 있다면 status 400 띄우기
            post_serializer.save()
            return Response({"message": "Post가 성공적으로 생성됐습니다."})
        else:
            return Response({"error": post_serializer.errors}, status=400)

    def delete(self, request, post_id):
        post = get_object_or_404(Post, pk=post_id)
        user = request.user
        if post.author != user:
            return Response({"detail": "권한이 없습니다."}, status=status.HTTP_403_FORBIDDEN)
        post.delete()
        return Response({"detail": "삭제되었습니다"}, status=status.HTTP_200_OK)
