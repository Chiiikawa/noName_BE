from django.db import models
from no_name.settings import AUTH_USER_MODEL



# Create your models here.
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
    )
    author = models.ForeignKey(
        AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="comments",
    )
    content = models.CharField("content", max_length=150)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
   
class Products(models.Model):
    posting = models.ForeignKey(
    Post,
    on_delete=models.CASCADE,
    related_name="products",
    )
    productsize = models.CharField("content", max_length=10)
    productframe =models.ForeignKey(ProductFrame, blank=True, null=True)
    cart = models.ManyToManyField(AUTH_USER_MODEL, related_name="cartitems")

class ProductFrame(models.Model):
    frametitle = model.CharField("title", max_length=20)
    frame = models.ImageField(
        upload_to="media/frameimage",
        blank=True,
        null=True,
    )
    
