from django.urls import path
from . import views

urlpatterns = [
    # 게시물 조회/생성
    path("", views.PostView.as_view(), name="posts"),
    # 게시물 상세/삭제
    path("<int:post_id>/", views.PostView.as_view(), name="post_detail"),
    # 좋아요
    path("<int:post_id>/likes/", views.LikesView.as_view(), name="likes"),
    # 댓글 조회/등록
    path("<int:post_id>/comments/", views.CommentsView.as_view(), name="comments"),
    # apikey 요청
    #path("image/", views.ImageView.as_view(), name="image"),
    # 상품 조회/구매
    path("<int:post_id>/product/", views.ProductView.as_view(), name="comments"),

]

