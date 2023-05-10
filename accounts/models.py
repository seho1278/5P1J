from django.db import models
from django.contrib.auth.models import AbstractUser
from taggit.managers import TaggableManager
from imagekit.models import ProcessedImageField
from imagekit.processors import ResizeToFill

# Create your models here.
class User(AbstractUser):
    followings = models.ManyToManyField('self', related_name='followers', symmetrical=False)
    birthday = models.DateField(null=True, blank=True)
    tags = TaggableManager(blank=True)
