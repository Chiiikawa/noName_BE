from rest_framework import serializers
from .models import Like, Comment, Post, Bookmark

class BookmarkSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bookmark
        fields = ('id', 'user', 'post')

#BaseInteractionSerializer을 만들어서 아래 LikeSerializer,CommentSerializer에서 중복값을 줄임
class BaseInteractionSerializer(serializers.ModelSerializer):
    author = serializers.SerializerMethodField()
    class Meta:
        abstract = True

class LikeSerializer(BaseInteractionSerializer):
    class Meta(BaseInteractionSerializer.Meta):
        model = Like
        fields = ['id', 'user', 'post']
        
class CommentSerializer(BaseInteractionSerializer):
    class Meta(BaseInteractionSerializer.Meta):
        model = Comment
        fields = ['id', 'post', 'user', 'content', 'created_at']

#CommentCreateSerializer는 CommentSerializer을 종속받아 중복값을 줄임
class CommentCreateSerializer(CommentSerializer):
    class Meta(CommentSerializer.Meta):
        fields = ("post", "content")

class PostCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ['author', 'title', 'content', 'generated_image']

        def validate_generated_image(self, value):
        # Ensure that a generated image is provided
            if not value:
                raise serializers.ValidationError("A generated image is required.")
            return value

class PostListSerializer(serializers.ModelSerializer):
    author = serializers.SerializerMethodField()

    def get_author(self, obj):
        return {
            "id": obj.author.pk,
            "nickname": obj.author.nickname,
        }

    class Meta:
        model = Post
        fields = (
            "id",
            "author",
            "generated_image",
            "created_at",
        )


class PostDetailSerializer(serializers.ModelSerializer):
    author = serializers.SerializerMethodField()
    likes = LikeSerializer(many=True, read_only=True)
    comments = CommentSerializer(many=True, read_only=True)

    def get_author(self, obj):
        return {
            "id": obj.author.pk,
            "nickname": obj.author.nickname,
        }

    class Meta:
        model = Post
        fields = (
            "generated_image",
            "author",
            "title",
            "content",
            "likes",
            "comments",
        )