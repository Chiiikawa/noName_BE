from django.db import models
from accounts.models import User
from no_name import settings

class Post(models.Model):
    title = models.CharField(max_length=100)
    content = models.TextField()
    
class Like(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    
    class Meta:
        unique_together = ('user', 'post')
    
class Comment(models.Model):
    post = models.ForeignKey(Post, related_name='comments', on_delete=models.CASCADE)   # Post 모델과 외래키 관계를 형성
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)    # User 모델과 외래키 관계를 형성
    content = models.TextField() # 댓글 내용을 저장하는 필드
    created_at = models.DateTimeField(auto_now_add=True)    # 댓글 생성 시간을 자동으로 저장하는 필드.