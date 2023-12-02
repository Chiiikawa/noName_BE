# Django, rest_framework 관련
from django.shortcuts import get_object_or_404
from django.db.models import Count, F
from django.core.files.base import ContentFile
from rest_framework import viewsets, status, permissions, generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import APIView, permission_classes, action

# Python 기본
import requests
import random
from datetime import datetime

# Project와 app 내부
from accounts.models import History
from no_name.settings import API_REQUEST_POINT, AUTH_USER_MODEL
from .models import Post, Like, Comment, Bookmark
from .serializers import (
    LikeSerializer, 
    CommentSerializer, 
    CommentCreateSerializer, 
    PostCreateSerializer, 
    PostListSerializer, 
    PostDetailSerializer, 
    BookmarkSerializer,
)
from .dalle import generate_image



class BookmarkView(APIView):
    queryset = Bookmark.objects.all()
    serializer_class = BookmarkSerializer

    # bookmark 생성/삭제
    def post(self, request, post_id):
        user = request.user
        post = get_object_or_404(Post, pk=post_id)

        existing_bookmark = Bookmark.objects.filter(user=user, post=post).first()   # 사용자가 해당 post에 bookmark를 눌렀는지 조회
        if existing_bookmark:
            existing_bookmark.delete()  # 사용자와 post간 bookmark instance가 있다면, post request가 들어오면 bookmark instance 삭제
            return Response({"messsage": "댓글 삭제 성공"}, 
                            status=status.HTTP_200_OK
                            )
        # Bookmark 추가
        Bookmark.objects.create(user=user, post=post)   # 사용자와 post간 bookmark instance가 있다면, bookmark instance 생성
        return Response(
            {"messsage": "댓글 생성 성공"}, 
            status=status.HTTP_200_OK
        )


class LikeView(APIView):
    queryset = Like.objects.all()
    serializer_class = LikeSerializer

    def post(self, request, post_id):
        # request.user는 현재 로그인한 사용자를 나타냅니다.
        user = request.user
        post = get_object_or_404(Post, pk=post_id)

        existing_like = Like.objects.filter(user=user, post=post).first()   # 사용자가 해당 post에 ㅣlike를 눌렀는지 조회
        if existing_like:   # 사용자와 post간 like instance가 있다면, post request가 들어오면 like instance 삭제
            existing_like.delete()
            return Response(
                {"likes_count": post.likes.count(), "is_liked": False}, status=status.HTTP_200_OK
            )
        Like.objects.create(user=user, post=post)   # 사용자와 post간 like instance가 있다면, post request 시 like instance 삭제
        return Response(
            {"likes_count": post.likes.count(), "is_liked": True}, status=status.HTTP_200_OK
        )

class CommentView(APIView):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer

    def post(self, request, post_id):   # 댓글 생성
        post = get_object_or_404(Post, pk=post_id)
        user = request.user
        serializer = CommentCreateSerializer(data=request.data)
        
        if serializer.is_valid():
            serializer.save(user=user, post=post)
            return Response(
                {"data": serializer.data,}, status=status.HTTP_200_OK
            )
        return Response(
            {"detail": "유효하지 않은 댓글", "errors": serializer.errors}, 
            status=status.HTTP_400_BAD_REQUEST
            )
    
    
# DALL-E API에 요청을 보내서 Image를 생성한 후, 이미지의 URL을 받아오는 View
class DalleAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    def post(self, request, *args, **kwargs):
        prompt = request.data.get('prompt') # frontend request에서 prompt라는 데이터를 추출
        user = request.user
        if user.point < API_REQUEST_POINT:  # 사용자가 보유한 point가 요청 포인트(1)보다 작을 경우, status 403을 return
            return Response({"detail": "포인트가 부족합니다."}, status=status.HTTP_403_FORBIDDEN)
        user.point = F("point") - API_REQUEST_POINT
        user.save()
        user.refresh_from_db()  # Django의 query expression F()를 사용한 후에는 refresh_from_db() 사용해서 
        History.objects.create(user=user, action="create", point=user.point)
        if not prompt:  # prompt가 비어있거나 없는 경우를 확인.
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
            
            # Bookmark 정보 가져오기
            bookmark_queryset = Bookmark.objects.filter(post=post)
            bookmark_serializer = BookmarkSerializer(bookmark_queryset, many=True) #가져온 정보를 직렬화

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
            data["bookmark"] = bookmark_serializer.data
            
            if user.is_authenticated and post.likes.filter(user=user).exists():
                data["is_liked"] = True
            else:
                data["is_liked"] = False

            if user.is_authenticated and post.bookmark.filter(user=user).exists():
                data["is_bookmarked"] = True
            else:
                data["is_bookmarked"] = False

            return Response(data, status=status.HTTP_200_OK) #직렬화된 데이터와 함께 HTTP 200 OK 상태 코드를 갖는 응답을 반환

        posts = (
            Post.objects.all() #모든 게시물을 가져오는데, select_related를 사용하여 게시물의 작성자 정보를 미리 가져옴
            .order_by("id") #order_by로 게시물을 최신순으로 정렬
        )
        serializer = PostListSerializer(posts, many=True) #가져온 게시물들을 PostListSerializer를 사용하여 직렬화
        return Response(serializer.data, status=status.HTTP_200_OK) #직렬화된 데이터와 함께 HTTP 200 OK 상태 코드를 갖는 응답을 반환합니다. 이는 전체 게시물 목록을 나타냄

    def post(self, request):
        user = request.user
        image_url = request.data["image_url"]
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
        return Response({"error": post_serializer.errors}, status=400)

    def delete(self, request, post_id):
        post = get_object_or_404(Post, pk=post_id)
        user = request.user
        if post.author != user:
            return Response({"detail": "권한이 없습니다."}, status=status.HTTP_403_FORBIDDEN)
        post.delete()
        return Response({"detail": "삭제되었습니다"}, status=status.HTTP_200_OK)