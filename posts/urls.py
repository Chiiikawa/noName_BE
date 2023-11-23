from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from .views import LikeViewSet, CommentViewSet, DalleAPIView
from django.contrib import admin


router = DefaultRouter()
router.register(r'likes', LikeViewSet)
router.register(r'comments', CommentViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('dalle/', DalleAPIView.as_view(), name='dalle-api'),
]