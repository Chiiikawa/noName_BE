from rest_framework import serializers
from .models import Like, Comment, Post

class LikeSerializer(serializers.ModelSerializer):
     class Meta:
         model = Like
         fields = ['id', 'user', 'post']
        
class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ['id', 'post', 'user', 'content', 'created_at']

class PostCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ['author', 'title', 'content', 'generated_image']

    def validate_generated_image(self, value):
        # Ensure that a generated image is provided
        if not value:
            raise serializers.ValidationError("A generated image is required.")
        return value