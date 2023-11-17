from rest_framework import serializers
from .models import Post, Comment, Products, ProductFrame


class PostListSerializer(serializers.ModelSerializer):
    author = serializers.SerializerMethodField()
    likes_count = serializers.IntegerField()

    def get_author(self, obj):
        return {
            "id": obj.author.pk,
            "username": obj.author.username,
        }

    class Meta:
        model = Post
        fields = (
            "id",
            "author",
            "image",
            "likes_count",
        )


class PostDetailSerializer(serializers.ModelSerializer):
    author = serializers.SerializerMethodField()
    likes_count = serializers.IntegerField()
    comments_count = serializers.IntegerField()
    # 이미지 URL 필드 추가
    image_url = serializers.SerializerMethodField()

    def get_author(self, obj):
        return {
            "id": obj.author.pk,
            "username": obj.author.username,
        }

    class Meta:
        model = Post
        fields = (
            'id', 
            'author', 
            'image', 
            'image_url',            
            "created_at",
            "likes_count",
            "comments_count"
        )
    def get_image_url(self, obj):
        if obj.image:
            return self.context['request'].build_absolute_uri(obj.image.url)
        return None

class PostCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ("image", "content")


class CommentListSerializer(serializers.ModelSerializer):
    author = serializers.SerializerMethodField()

    def get_author(self, obj):
        return {"username": obj.author.username, "id": obj.author.id}

    class Meta:
        model = Comment
        fields = ("author", "content", "created_at")


class CommentCreateSerializer(serializers.ModelSerializer):
    author = serializers.SerializerMethodField()

    def get_author(self, obj):
        return {"username": obj.author.username, "id": obj.author.id}

    class Meta:
        model = Comment
        fields = ("content", "author")
        

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ("image", "productsize")


class ProductFrameSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ("image", "frame") #framecolor?
        

