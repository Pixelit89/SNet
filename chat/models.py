from django.db import models
from django.contrib.auth.models import User
# Create your models here.


class ExtendedUser(User):
    avatar = models.ImageField(upload_to='avatars/', default='avatars/default.png')
    friends = models.ManyToManyField('self', related_name='friends', blank=True)
