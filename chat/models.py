from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

import os


# Create your models here.
def get_upload_to(instance, filename):
    return os.path.join('gallery', str(instance.user.id), filename)


class ExtendedUser(User):
    avatar = models.ImageField(upload_to='avatars/', default='avatars/default.png')
    friends = models.ManyToManyField('self', related_name='friends', blank=True)


class FriendsRequest(models.Model):
    user = models.ForeignKey(ExtendedUser, on_delete=models.CASCADE)
    friend_request = models.IntegerField()


class ChatGroups(models.Model):
    name = models.CharField(max_length=255)
    users = models.ManyToManyField(ExtendedUser, related_name=None)

    def __str__(self):
        return self.name


class Gallery(models.Model):
    pic = models.ImageField(upload_to=get_upload_to)
    pub_date = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(ExtendedUser, on_delete=models.CASCADE)


class Wall(models.Model):
    message = models.TextField()
    pub_date = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey(ExtendedUser, on_delete=models.CASCADE)
    wall_owner = models.IntegerField()


class ChatMessages(models.Model):
    user = models.ForeignKey(ExtendedUser, on_delete=models.CASCADE)
    message = models.TextField()
    pub_date = models.DateTimeField(auto_now_add=True)
    chat_room = models.ForeignKey(ChatGroups, on_delete=models.CASCADE)

    def __str__(self):
        return self.user.username
