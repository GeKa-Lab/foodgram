from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator


UNIQUE_USERNAME = RegexValidator(r'^[\w.@+-]+\Z', 'Поддерживаемые знаки.')
REGEX_SLUG = RegexValidator(r'^[-a-zA-Z0-9_]+$', 'Поддерживаемые знаки.')
REGEX_AMOUNT = RegexValidator(r'^[1-9][0-9]*$', 'Поддерживаемые значения.')


# Create your models here.
class User(AbstractUser):
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = [
        'username',
        'first_name',
        'last_name',
    ]

    email = models.EmailField(
        unique=True,
        max_length=254,
        verbose_name='E-mail пользователя',
        help_text='Укажите e-mail пользователя'
    )
    username = models.CharField(
        unique=True,
        max_length=150,
        validators=[UNIQUE_USERNAME],
        verbose_name='Юзернейм пользователя',
        help_text='Укажите юзернейм пользователя'
    )
    first_name = models.CharField(
        max_length=150,
        verbose_name='Имя пользователя',
        help_text='Укажите имя пользователя'
    )
    last_name = models.CharField(
        max_length=150,
        verbose_name='Фамилия пользователя',
        help_text='Укажите фамилию пользователя'
    )

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ('id',)

    def __str__(self):
        return self.username


class Subscriber(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='authors',
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='subscribers',
    )

    class Meta:
        ordering = ('author',)

    def __str__(self):
        return f"{self.author} - {self.user}"
