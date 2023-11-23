from django.contrib import admin
from posts.models import GeneratedImage, Post, Comment

# Register your models here.
admin.site.register(GeneratedImage)
admin.site.register(Post)
admin.site.register(Comment)