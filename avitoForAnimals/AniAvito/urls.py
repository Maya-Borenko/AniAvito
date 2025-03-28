from django.contrib import admin
from django.urls import path
from  . import views
from django.contrib.auth import views as auth_views


urlpatterns = [
    path('', views.home, name='home'),
    path('auth/', views.auth_view, name='auth'),
    path('logout/', auth_views.LogoutView.as_view(next_page='home'), name='logout'),
    path('cabinet/', views.cabinet, name='cabinet'),
    path('posts/', views.posts, name='posts'),

    #path('login/', views.login, name='login'),
    #path('logout/', auth_views.LogoutView.as_view(next_page='home'), name='logout'),
]