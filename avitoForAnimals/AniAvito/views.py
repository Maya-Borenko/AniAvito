import os
from django.conf import settings
from django.shortcuts import render, redirect
from .forms import UserRegistrationForm, UserEditForm
from django.contrib.auth import login as auth_login
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.core.files.storage import default_storage
from .models import Post
from django.db.models import Q

def home(request):
    return render(request, 'home.html')



def posts(request):
    # Инициализация переменных для фильтрации
    query = request.GET.get('search', '')
    post_type = request.GET.get('type', '')

    # Фильтрация объявлений
    posts = Post.objects.all()

    if query:
        posts = posts.filter(Q(name__icontains=query) | Q(type__icontains=query))  # Поиск по названию и типу

    if post_type:
        posts = posts.filter(type=post_type)  # Фильтрация по типу

    return render(request, 'posts.html', {'posts': posts})

def auth_view(request):
    form_register = UserRegistrationForm()
    form_login = AuthenticationForm()
    active_tab = 'login'

    if request.method == 'POST':
        if 'register' in request.POST:
            form_register = UserRegistrationForm(request.POST)
            if form_register.is_valid():
                user = form_register.save()
                auth_login(request, user)
                return redirect('home')
            else:
                active_tab = 'register'
                form_login = AuthenticationForm()
                return render(request, 'auth.html', {'form_register': form_register, 'form_login': form_login, 'active_tab': active_tab})
        elif 'login' in request.POST:
            form_login = AuthenticationForm(request, data=request.POST)
            if form_login.is_valid():
                user = form_login.get_user()
                auth_login(request, user)
                return redirect('home')
            else:
                form_register = UserRegistrationForm()
                return render(request, 'auth.html', {'form_register': form_register, 'form_login': form_login, 'active_tab': active_tab})

    return render(request, 'auth.html', {'form_register': form_register, 'form_login': form_login, 'active_tab': active_tab})

@login_required
def cabinet(request):
    if request.method == 'POST':
        old_image = request.user.user_image
        form = UserEditForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            new_image = request.user.user_image

            if old_image != new_image and old_image: 
                old_image_path = old_image.path  
                if os.path.isfile(old_image_path):
                    default_storage.delete(old_image_path)

            return redirect('cabinet') 

    else:
        form = UserEditForm(instance=request.user)

    return render(request, 'cabinet.html', {'form': form})
