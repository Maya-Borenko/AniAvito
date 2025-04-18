from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User, Post
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model

class UserRegistrationForm(UserCreationForm):
    first_name = forms.CharField(
        label=_("Имя"),
        max_length=30,
        widget=forms.TextInput(attrs={'placeholder': _('Ваше имя')}),
    )
    last_name = forms.CharField(
        label=_("Фамилия"),
        max_length=150,
        widget=forms.TextInput(attrs={'placeholder': _('Ваша фамилия')}),
    )
    email = forms.EmailField(
        label=_("Email"),
        widget=forms.EmailInput(attrs={'placeholder': _('example@example.com')}),
    )
    password1 = forms.CharField(
        label=_("Пароль"),
        widget=forms.PasswordInput(attrs={'placeholder': _('Введите пароль')}),
    )
    password2 = forms.CharField(
        label=_("Подтверждение пароля"),
        widget=forms.PasswordInput(attrs={'placeholder': _('Повторите пароль')}),
    )

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'password1', 'password2']

    def save(self, commit=True):
        user = super().save(commit=False)
        if commit:
            user.save()
        return user
    
    def clean_password_confirmation(self):
        password = self.cleaned_data.get('password')
        password_confirmation = self.cleaned_data.get('password_confirmation')
        if password != password_confirmation:
            raise forms.ValidationError("Пароли не совпадают!")
        return password_confirmation
    

class UserEditForm(forms.ModelForm):
    User = get_user_model()
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'user_image']

class PostForm(forms.ModelForm):
    PREDEFINED_TYPES = [
        'Собака',
        'Кошка',
        'Птица',
        'Грызун',
        'Другое'
    ]

    type = forms.CharField(
        label='Тип',
        widget=forms.TextInput(attrs={
            'list': 'animal-types',
            'placeholder': 'Выберите или введите свой'
        })
    )

    class Meta:
        model = Post
        fields = ['name', 'type', 'description', 'photo', 'file']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Опишите ваше объявление...'}),
        }

class PostEditForm(forms.ModelForm):
    PREDEFINED_TYPES = [
        'Собака',
        'Кошка',
        'Птица',
        'Грызун',
        'Другое'
    ]
    
    type = forms.CharField(
        label='Тип',
        widget=forms.TextInput(attrs={
            'list': 'animal-types',
            'placeholder': 'Выберите или введите свой тип'
        })
    )
    
    class Meta:
        model = Post
        fields = ['name', 'type', 'description', 'photo', 'file'] 
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Опишите ваше объявление...'}),
        }

    def clean_type(self):
        type = self.cleaned_data.get('type')
        if not type:
            raise forms.ValidationError("Выберите тип животного или введите свой.")
        return type

class MessageForm(forms.Form):
    message = forms.CharField(widget=forms.Textarea, required=True)