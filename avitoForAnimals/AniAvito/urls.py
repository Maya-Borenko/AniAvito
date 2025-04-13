from django.contrib import admin
from django.urls import path
from  . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.home, name='home'),
    path('auth/', views.auth_view, name='auth'),
    path('logout/', auth_views.LogoutView.as_view(next_page='home'), name='logout'),
    path('cabinet/', views.cabinet, name='cabinet'),
    path('cabinet/<int:user_id>/', views.cabinet, name='user_cabinet'),
    path('posts/', views.posts, name='posts'),
    path('posts/create/', views.create_post, name='create_post'),
    path('favorites/', views.favorites, name='favorites'),
    path('toggle_favorite/<int:post_id>/', views.toggle_favorite, name='toggle_favorite'),
    path('delete_post/<int:post_id>/', views.delete_post, name='delete_post'),
    path('chats/', views.all_chats_view, name='all_chats'),
    path('chat/<int:chat_id>/', views.chat_view, name='chat_view'),
    path('create_or_get_chat/<int:post_id>/<int:user_id>/', views.create_or_get_chat, name='create_or_get_chat'),
]