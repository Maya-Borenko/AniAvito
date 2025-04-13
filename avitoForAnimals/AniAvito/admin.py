from django.contrib import admin
from .models import User, Post, Review, Chat, Message

# Настройки для модели User
@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('email', 'first_name', 'last_name', 'is_staff', 'is_active', 'date_joined')

# Настройки для модели Post
@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'type', 'status', 'date')

# Настройки для модели Review
@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('user', 'post', 'review_time')

# Настройки для модели Chat
@admin.register(Chat)
class ChatAdmin(admin.ModelAdmin):
    list_display = ('user', 'post')
    search_fields = ('user__email', 'post__name')
    list_per_page = 20

# Настройки для модели Message
@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('user', 'chat', 'send_time')
    list_filter = ('send_time',)
    search_fields = ('message',)
    ordering = ('-send_time',)
    list_per_page = 20