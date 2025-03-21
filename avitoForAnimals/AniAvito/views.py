from django.shortcuts import render, redirect
from .forms import UserRegistrationForm, UserEditForm
from django.contrib.auth import login as auth_login
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required

def home(request):
    return render(request, 'home.html')

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
        form = UserEditForm(request.POST, request.FILES, instance=request.user) #Добавьте request.FILES для обработки файлов
        if form.is_valid():
            form.save()
            return redirect('cabinet')
    else:
        form = UserEditForm(instance=request.user)
    return render(request, 'cabinet.html', {'form': form})