from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model
from django.db.models import Q
from django.utils import timezone
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import AbstractUser, Group, Permission

class Category(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name
    

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)
    username = models.CharField(max_length=255, unique=True)
    last_seen = models.DateTimeField(default=timezone.now)
    is_typing = models.BooleanField(default=False)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)

    def __str__(self):
        return self.user.username

    @property
    def avatar_url(self):
        if self.avatar and hasattr(self.avatar, 'url'):
            return self.avatar.url
        else:
            return '/static/default/avatar.png'
    


class PrivateChat(models.Model):
    participants = models.ManyToManyField(User, related_name='chats')

    def __str__(self):
        return f"Chat between {', '.join(user.username for user in self.participants.all())}"


class PrivateMessage(models.Model):
    chat = models.ForeignKey(PrivateChat, related_name='messages', on_delete=models.CASCADE)
    sender = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField()
    file = models.FileField(upload_to='private_messages/', null=True, blank=True)
    timestamp = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f'{self.sender} at {self.timestamp}'

class DeletedChat(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    chat = models.ForeignKey(PrivateChat, on_delete=models.CASCADE)


class CustomUser(AbstractUser):
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)

    # Specify related_name to avoid conflicts
    groups = models.ManyToManyField(Group, related_name='customuser_set', blank=True)
    user_permissions = models.ManyToManyField(Permission, related_name='customuser_set', blank=True)

class Photo(models.Model):
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
    image = models.ImageField(upload_to='photos/')
    description = models.TextField()

    def __str__(self):
        return self.description
    

class Post(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    description = models.TextField()
    photos = models.ManyToManyField(Photo, related_name='posts')
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    image = models.ImageField(upload_to='posts/', null=True, blank=True)
    username = models.CharField(max_length=100) 
    city = models.CharField(max_length=255, null=True, blank=True)
    state = models.CharField(max_length=255, null=True, blank=True)  # Add this line
    country = models.CharField(max_length=255, null=True, blank=True)
    latitude = models.FloatField(null=True, blank=True)  # Add this line
    longitude = models.FloatField(null=True, blank=True) 
    updated_at = models.DateTimeField(auto_now=True)



    def __str__(self):
        return self.title
    
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    country = models.CharField(max_length=100, blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    state = models.CharField(max_length=100, blank=True, null=True)
    latitude = models.FloatField(blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)

    def __str__(self):
        return self.user.username