from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.contrib.auth.models import PermissionsMixin
from django.core.mail import send_mail
from django.db import models

# Менеджер пользователей
class CustomUserManager(BaseUserManager):
    def create_user(self, email, first_name, last_name, password=None, **extra_fields):
        if not email:
            raise ValueError("У пользователя должен быть указан email")
        email = self.normalize_email(email)
        user = self.model(email=email, first_name=first_name, last_name=last_name, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, first_name, last_name, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Суперпользователь должен иметь is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Суперпользователь должен иметь is_superuser=True.')

        return self.create_user(email, first_name, last_name, password, **extra_fields)

# Модель пользователя
class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField("Email", unique=True)
    first_name = models.CharField("Имя", max_length=30, null=True, blank=True)
    last_name = models.CharField("Фамилия", max_length=30, null=True, blank=True)
    date_joined = models.DateTimeField("Дата регистрации", auto_now_add=True)
    is_active = models.BooleanField("Активен", default=True)
    password = models.CharField("Пароль", max_length=100, blank=True)
    username = models.CharField("Имя пользователя", max_length=30, blank=True)
    user_image = models.FileField(upload_to="User_image/", null=True, blank=True, verbose_name="Фото профиля")
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["first_name", "last_name"]

    objects = CustomUserManager()

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"

    def get_full_name(self):
        """Возвращает полное имя (имя + фамилия)."""
        return f"{self.first_name} {self.last_name}".strip()

    def get_short_name(self):
        """Возвращает короткое имя."""
        return self.first_name

    def email_user(self, subject, message, from_email=None, **kwargs):
        """Отправляет письмо пользователю."""
        send_mail(subject, message, from_email, [self.email], **kwargs)

# Модель поста
class Post(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Пользователь")
    name = models.CharField("Название", max_length=20)
    type = models.CharField("Тип", max_length=200)
    file = models.FileField(upload_to="Document/", null=True, blank=True, verbose_name="Файл")
    date = models.DateTimeField("Время публикации", auto_now_add=True)
    status = models.BooleanField("Открыто", default=True)

    class Meta:
        verbose_name = "Пост"
        verbose_name_plural = "Посты"

# Модель отзыва
class Review(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Пользователь")
    post = models.ForeignKey(Post, on_delete=models.CASCADE, verbose_name="Пост")
    review_text = models.TextField("Текст отзыва")
    review_time = models.DateTimeField("Время отзыва", auto_now_add=True)

    class Meta:
        verbose_name = "Отзыв"
        verbose_name_plural = "Отзывы"

# Модель чата
class Chat(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Пользователь")
    post = models.ForeignKey(Post, on_delete=models.CASCADE, verbose_name="Пост")

    class Meta:
        verbose_name = "Чат"
        verbose_name_plural = "Чаты"

# Модель сообщения
class Message(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Пользователь")
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE, verbose_name="Чат")
    message = models.TextField("Текст сообщения")
    send_time = models.DateTimeField("Время отправки", auto_now_add=True)

    class Meta:
        verbose_name = "Сообщение"
        verbose_name_plural = "Сообщения"
