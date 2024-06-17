from django.urls import path
from . views import *


urlpatterns = [
    path('', home, name='home'), 
    path('login/', login_view, name='login'),
    path('signup', signup, name="signup"),
    path('dashboard/', dashboard, name='dashboard'),
    path('create_post/', create_post, name='create_post'),
    path('post/<int:post_id>/', view_post, name='view_post'),
    path('logout/', logout_user, name='logout'),
    path('portfolio/', portfolio, name='portfolio'),
    path('my_posts/', my_posts, name='my_posts'),
    path('post/<int:post_id>/delete/', delete_post, name='delete_post'),
    path('post/<int:post_id>/edit/', edit_post, name='edit_post'),
    path('search/', search, name='search'),
    path('portfolio2/<int:user_id>/', portfolio2, name='portfolio2'),
    path('chats/', chat_list, name='chat_list'),
    path('private_chat/<int:chat_id>/', private_chat, name='private_chat'),
    path('start_private_chat/<int:user_id>/', start_private_chat, name='start_private_chat'),
    path('chats/delete/', delete_chat, name='delete_chat'),
]




