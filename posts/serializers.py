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

    def get_author(self, obj):
        return {
            "id": obj.author.pk,
            "username": obj.author.username,
        }

    def get_answer_len(self, obj):
        return len(obj.correct_answer)

    class Meta:
        model = Post
        fields = (
            "image",
            "author",
            "created_at",
            "updated_at",
            "likes_count",
            "comments_count",
        )


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
