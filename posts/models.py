from django.db import models
from accounts.models import User
from no_name.settings import AUTH_USER_MODEL


class Post(models.Model):
    generated_image = models.ImageField(
        upload_to="dalle-image",
        blank=True,
        null=True,
    )
    title = models.CharField(max_length=100)
    content = models.TextField()

    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)
    author = models.ForeignKey(AUTH_USER_MODEL, related_name='posts', null=True, on_delete=models.CASCADE)
    
class Like(models.Model):
    user = models.ForeignKey(AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='likes_of_user')
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='likes_of_post')
    
    class Meta:
        unique_together = ('user', 'post')
    
class Comment(models.Model):
    post = models.ForeignKey(Post, related_name='comments', on_delete=models.CASCADE)   # Post 모델과 외래키 관계를 형성
    user = models.ForeignKey(AUTH_USER_MODEL, on_delete=models.CASCADE)    # User 모델과 외래키 관계를 형성
    content = models.TextField() # 댓글 내용을 저장하는 필드
    created_at = models.DateTimeField(auto_now_add=True)    # 댓글 생성 시간을 자동으로 저장하는 필드.
    