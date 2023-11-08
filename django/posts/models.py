from django.db import models
from no_name.settings import AUTH_USER_MODEL

class Post(models.Model):
    author = models.ForeignKey(
        AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="posts",
        null = True,
    )
    image = models.ImageField(
        upload_to="media/postimage",
        default="media/postimage/defaultpostimage.png",
        blank=True,
        null=True,
    )
    content = models.CharField("content", max_length=300)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    bookmark = models.ManyToManyField(AUTH_USER_MODEL, blank=True, related_name='bookmark')
    likes = models.ManyToManyField(AUTH_USER_MODEL, blank=True, related_name='likes')

class Comment(models.Model):
    posting = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name="comments",
        null=True,
    )
    author = models.ForeignKey(
        AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="comments",
        null=True,
    )
    content = models.CharField("content", max_length=150)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class ProductFrame(models.Model):
    frametitle = models.CharField("title", max_length=20)
    frame = models.ImageField(
        upload_to="media/frameimage",
        blank=True,
        null=True,
    )
   
class Products(models.Model):
    posting = models.ForeignKey(
    Post,
    on_delete=models.CASCADE,
    related_name="products",
    )
    productsize = models.CharField("content", max_length=10)
    #ForeignKey 의 AUTH_USER_MODEL 맞는지 확인
    productframe = models.ForeignKey(ProductFrame, on_delete=models.SET_NULL, blank=True, null=True)
    cart = models.ManyToManyField(AUTH_USER_MODEL, related_name="cartitems")