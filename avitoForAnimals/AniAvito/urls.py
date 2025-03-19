from django.contrib import admin
from django.urls import path
from  . import views

urlpatterns = [
    path('', views.home, name='home'),
    #path('login/', views.login, name='login'),
    #path('logout/', auth_views.LogoutView.as_view(next_page='home'), name='logout'),
    path('register/', views.register, name='register'),
]