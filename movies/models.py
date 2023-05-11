from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from taggit.managers import TaggableManager
from imagekit.models import ProcessedImageField
from imagekit.processors import ResizeToFill

# Create your models here.
class Post(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    title = models.CharField(max_length=20)
    description = models.CharField(max_length=300)
    want_users = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='want_posts')
    watching_users = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='watching_posts')
    platform = models.URLField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

# class PostImage(models.Model):
#     post = models.ForeignKey(Post, on_delete=models.CASCADE)
#     image = ProcessedImageField(blank=True, upload_to='', processors=[ResizeToFill(500, 350)], format='JPEG', options={'quality':100})


class Review(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    content = models.CharField(max_length=500)
    rating = models.PositiveBigIntegerField(default=3, validators=[MinValueValidator(0), MaxValueValidator(5)])
    tags = models.CharField(max_length=100, default='태그')
    like_users = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='like_reviews')

class Comment(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    review = models.ForeignKey(Review, on_delete=models.CASCADE, related_name='reviews')
    content = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)
    like_users = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='like_comments')
    updated_at = models.DateTimeField(auto_now=True)
