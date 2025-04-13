import os
from django.shortcuts import render, get_object_or_404, redirect
from .models import User, Favorite, Post, Chat, Post, Message, Review
from .forms import UserRegistrationForm, UserEditForm, PostForm, PostEditForm
from django.contrib.auth import login as auth_login
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.core.files.storage import default_storage
from django.db.models import Q, OuterRef, Subquery
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.utils import timezone

def home(request):
    return render(request, 'home.html')


def posts(request):
    query = request.GET.get('search', '')
    post_type = request.GET.get('type', '')

    post_types = Post.objects.values_list('type', flat=True).distinct()

    posts = Post.objects.filter(status=True)


    if request.user.is_authenticated:
        for post in posts:
            post.is_favorite = Favorite.objects.filter(user=request.user, post=post).exists()


    if query:
        posts = posts.filter(Q(name__icontains=query) | Q(type__icontains=query))

    if post_type:
        posts = posts.filter(type=post_type)

    return render(request, 'posts.html', {'posts': posts, 'post_types': post_types})


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
def cabinet(request, user_id=None):
    if user_id:
        profile_user = get_object_or_404(User, id=user_id)
    else:
        profile_user = request.user

    is_owner = (request.user == profile_user)
    posts = Post.objects.filter(user=profile_user)
    reviews = Review.objects.filter(post__user=profile_user).select_related('user', 'post')


    if request.method == 'POST' and 'profile_form' in request.POST and is_owner:
        old_image = request.user.user_image
        form = UserEditForm(request.POST, request.FILES, instance=request.user)
        post_form = None
        if form.is_valid():
            form.save()
            new_image = request.user.user_image

            if old_image != new_image and old_image: 
                old_image_path = old_image.path  
                if os.path.isfile(old_image_path):
                    default_storage.delete(old_image_path)

            return redirect('cabinet') 

    elif request.method == 'POST' and 'post_form' in request.POST and is_owner:
        post_id = request.POST.get('post_id')
        post = get_object_or_404(Post, id=post_id, user=request.user)
        post_form = PostEditForm(request.POST, request.FILES, instance=post)
        form = None
        if post_form.is_valid():
            post_form.save()
            return redirect('cabinet') 
        else:
            print(post_form.errors)

    else:
        form = UserEditForm(instance=request.user) if is_owner else None
        post_form = PostEditForm() if is_owner else None

    return render(request, 'cabinet.html', {
        'form': form,
        'profile_user': profile_user,
        'is_owner': is_owner,
        'posts': posts,
        'post_form': post_form,
        'reviews': reviews
    })


@login_required
def create_post(request):
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.user = request.user  
            post.save()
            return redirect('posts') 
    else:
        form = PostForm()

    return render(request, 'create_post.html', {'form': form})


@csrf_exempt
@login_required
def toggle_favorite(request, post_id):
    try:
        post = Post.objects.get(id=post_id)
        favorite, created = Favorite.objects.get_or_create(user=request.user, post=post)
        
        if not created:
            favorite.delete()
            return JsonResponse({'success': True, 'is_favorite': False})
        else:
            return JsonResponse({'success': True, 'is_favorite': True})
    except Post.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Post not found'})
        
@login_required
def favorites(request):
    favorite_posts = Post.objects.filter(favorite__user=request.user)
    return render(request, 'favorites.html', {'favorite_posts': favorite_posts})

@csrf_exempt
def delete_post(request, post_id):
    if request.method == 'DELETE':
        post = get_object_or_404(Post, id=post_id)
        post.delete()
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'error'}, status=400)


def all_chats_view(request):
    chats = Chat.objects.filter(post__user=request.user) | Chat.objects.filter(user=request.user)
    
    latest_message_subquery = Message.objects.filter(
        chat=OuterRef('pk')
    ).order_by('-send_time')

    chats = chats.annotate(
        last_message_text=Subquery(latest_message_subquery.values('message')[:1]),
        last_message_time=Subquery(latest_message_subquery.values('send_time')[:1]),
        last_message_user=Subquery(latest_message_subquery.values('user__first_name')[:1])
    )
    return render(request, 'all_chats.html', {'chats': chats})

@login_required
def chat_view(request, chat_id=None):
    if chat_id:
        chat = Chat.objects.filter(id=chat_id).first()
        if not chat:
            chat = Chat.objects.create(post=post, user=request.user)
    else:
        chat = Chat.objects.create(post=post, user=request.user)

    post = chat.post
    messages = Message.objects.filter(chat=chat).order_by('send_time')

    is_owner = chat.post.user == request.user
    is_transaction_completed = not chat.post.status 
    can_write_review = not is_owner and is_transaction_completed

    existing_review = Review.objects.filter(post=post, user=request.user).first()
    
    if request.method == 'POST':
        message_text = request.POST.get('message')
        if message_text:
            Message.objects.create(
                user=request.user,
                chat=chat,
                message=message_text,
                send_time=timezone.now()
            )
            return redirect('chat_view', chat_id=chat.id)

        if 'complete_deal' in request.POST and is_owner:
            post.status = False 
            post.save()
            return redirect('chat_view', chat_id=chat.id)

        if 'write_review' in request.POST and can_write_review:
            return redirect('write_review', post_id=post.id, user_id=request.user.id)

        review_text = request.POST.get('review')
        if review_text and can_write_review:
            Review.objects.create(
                post=post,
                user=request.user,
                review_text=review_text,
                review_time=timezone.now()
            )
            return redirect('chat_view', chat_id=chat.id)
        
    return render(request, 'chat_view.html', {
        'chat': chat,
        'post': post,
        'messages': messages,
        'is_owner': is_owner,
        'can_write_review': can_write_review,
        'is_transaction_completed': is_transaction_completed,
        'existing_review': existing_review,
    })


def create_or_get_chat(request, post_id, user_id):
    post = Post.objects.get(id=post_id)   
    user = User.objects.get(id=user_id)  

    chat = Chat.objects.filter(post=post, user__in=[user, post.user]).distinct()

    if not chat.exists():
        chat = Chat.objects.create(post=post, user=user)  
    else:
        chat = chat.first() 

    return redirect('chat_view', chat_id=chat.id)