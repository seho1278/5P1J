from django.db import models
from django.contrib.auth.models import AbstractUser
from taggit.managers import TaggableManager
from imagekit.models import ProcessedImageField
from imagekit.processors import ResizeToFill

# Create your models here.
class User(AbstractUser):
    followings = models.ManyToManyField('self', related_name='followers', symmetrical=False)
    birthday = models.DateField(null=True, blank=True)
    # big_tags = models.CharField(max_length=100, default='태그')
    tags = models.CharField(max_length=10000, default='태그')
    image = models.ImageField(blank=True, upload_to='accounts/images/')
    reported = models.BooleanField(default=False)
