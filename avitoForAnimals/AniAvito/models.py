from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.contrib.auth.models import PermissionsMixin
from django.core.mail import send_mail
from django.db import models

# Create your models here.
class UserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, username, email, password, **extra_fields):
        if not email:
            raise ValueError('The given email must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.username = username
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, username, email, password=None, **extra_fields):
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(username, email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(email, password, **extra_fields)

class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(('email address'), unique=True)
    first_name = models.CharField(('first name'), null=True, max_length=30, blank=True)
    last_name = models.CharField(('last name'), null=True, max_length=30, blank=True)
    date_joined = models.DateTimeField(('date joined'), null=True, auto_now_add=True)
    is_active = models.BooleanField(('active'), default=True)
    password = models.CharField(('password'), max_length=100, blank=True)
    username = models.CharField(('username'), max_length=30, blank=True)
    user_image = models.FileField(upload_to='User_image/', null=True, verbose_name="")

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = ('user')
        verbose_name_plural = ('users')

    def get_full_name(self):
        '''
        Returns the first_name plus the last_name, with a space in between.
        '''
        full_name = '%s %s' % (self.first_name, self.last_name)
        return full_name.strip()

    def get_short_name(self):
        '''
        Returns the short name for the user.
        '''
        return self.first_name

    def email_user(self, subject, message, from_email=None, **kwargs):
        '''
        Sends an email to this User.
        '''
        send_mail(subject, message, from_email, [self.email], **kwargs)


class Post():
    id_user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(('Name'), max_length=20, auto_now_add=True)
    type = models.CharField(('Type'), max_length=200, auto_now_add=True)
    file = models.FileField(upload_to='Document/', null=True, verbose_name="")
    date = models.DateTimeField(('Post_time'), auto_now_add=True)
    status = models.BooleanField(('is_open'), default=True, auto_now_add=True)

class Review():
    id_user = models.ForeignKey(User, on_delete=models.CASCADE)
    id_post = models.ForeignKey(Post, on_delete=models.CASCADE)
    review_text = models.TextField(('Review_text'), auto_now_add=True)
    review_time = models.DateTimeField(('Review_time'), auto_now_add=True)

class Chat():
    id_user = models.ForeignKey(User, on_delete=models.CASCADE)
    id_post = models.ForeignKey(Post, on_delete=models.CASCADE)

class Message():
    id_user = models.ForeignKey(User, on_delete=models.CASCADE)
    id_chat = models.ForeignKey(Chat, on_delete=models.CASCADE)
    message = models.TextField(('Message_text'), auto_now_add=True)
    send_time = models.DateTimeField(('Message_time'), auto_now_add=True)
