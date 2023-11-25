from django.db import models
from accounts.models import User
from no_name.settings import AUTH_USER_MODEL

class GeneratedImage(models.Model):
    prompt = models.TextField() # 사용자가 입력한 프롬프트
    image_url = models.URLField(max_length=300) # 생성된 이미지 URL 을 generated_images로 저장
    author = models.ForeignKey(AUTH_USER_MODEL, related_name='generated_images', null=True, on_delete=models.CASCADE)
  

    def __str__(self):
        return self.prompt


class Post(models.Model):
    generated_image = models.ForeignKey(
        GeneratedImage,
        on_delete=models.SET_NULL,
        null=True,
    )
    title = models.CharField(max_length=100)
    content = models.TextField()

    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)
    author = models.ForeignKey(AUTH_USER_MODEL, related_name='posts', null=True, on_delete=models.CASCADE)
    
class Like(models.Model):
    user = models.ForeignKey(AUTH_USER_MODEL, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    
    class Meta:
        unique_together = ('user', 'post')
    
class Comment(models.Model):
    post = models.ForeignKey(Post, related_name='comments', on_delete=models.CASCADE)   # Post 모델과 외래키 관계를 형성
    user = models.ForeignKey(AUTH_USER_MODEL, on_delete=models.CASCADE)    # User 모델과 외래키 관계를 형성
    content = models.TextField() # 댓글 내용을 저장하는 필드
    created_at = models.DateTimeField(auto_now_add=True)    # 댓글 생성 시간을 자동으로 저장하는 필드.
    