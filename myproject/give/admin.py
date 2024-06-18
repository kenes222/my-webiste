from django.contrib import admin
from .models import *
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'username', 'avatar']



@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ['user', 'username', 'post_titles', 'created_at', 'country', 'city']

    def post_titles(self, obj):
        posts = Post.objects.filter(user=obj.user)
        return ", ".join([post.title for post in posts])
    post_titles.short_description = 'Post Titles'
