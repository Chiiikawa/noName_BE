from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from .views import LikeViewSet, CommentViewSet, DalleAPIView, PostCreateView, PostListView, PostDeleteView
from django.contrib import admin


router = DefaultRouter()
router.register(r'likes', LikeViewSet)
router.register(r'comments', CommentViewSet)
like_list = LikeViewSet.as_view({
'get': 'list',
'post': 'create'
})
like_detail = LikeViewSet.as_view({
'delete': 'destroy'
})

urlpatterns = [
    # 게시물 전체조회, 프롬프트 작성
    path('', PostListView.as_view(), name='main-page'),
    # dalle apikey 요청
    path('dalle/', DalleAPIView.as_view(), name='dalle-api'),
    # 게시물 작성
    path('create/', PostCreateView.as_view(), name='post-create'),
    # 특정 게시물 상세보기/삭제
    path('<int:post_id>/',PostListView.as_view(), name='post-detail'),
    # 특정 게시물 삭제
    path('<int:post_id>/delete/',PostDeleteView.as_view(), name='post-delete'),
    # 좋아요, 댓글 조회/등록
    path('interactions/',include(router.urls), name='like-comment'),
]