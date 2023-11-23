from rest_framework import serializers
from .models import Like, Comment

class LikeSerializer(serializers.ModelSerializer):
     class Meta:
         model = Like
         fields = ['id', 'user', 'post']
        
class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ['id', 'post', 'user', 'content', 'created_at']