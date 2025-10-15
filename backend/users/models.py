from django.contrib.auth.models import AbstractUser
from django.db import models
from foodgram.settings import EMAIL_MAX_LENGTH, NAME_MAX_LENGTH, REGEX_SIGNS


class User(AbstractUser):

    username = models.CharField(
        unique=True,
        max_length=NAME_MAX_LENGTH,
        validators=[REGEX_SIGNS],
        verbose_name='Никнейм пользователя',
        help_text='Укажите никнейм пользователя'
    )
    first_name = models.CharField(
        max_length=NAME_MAX_LENGTH,
        verbose_name='Имя пользователя',
        help_text='Укажите имя пользователя'
    )
    last_name = models.CharField(
        max_length=NAME_MAX_LENGTH,
        verbose_name='Фамилия пользователя',
        help_text='Укажите фамилию пользователя'
    )
    email = models.EmailField(
        unique=True,
        max_length=EMAIL_MAX_LENGTH,
        verbose_name='E-mail пользователя',
        help_text='Укажите e-mail пользователя'
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = [
        'username',
        'first_name',
        'last_name',
    ]

    class Meta:
        ordering = ('id',)
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    @property
    def admin(self):
        return self.role == self.ADMIN

    def __str__(self):
        return self.username


class Subscribers(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='authors',
        verbose_name='Автор рецептов',
        help_text='Укажите автора рецепта'
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='subscribers',
        verbose_name='Пользователь-подписчик',
        help_text='Укажите пользователя-подписчика'
    )

    class Meta:
        ordering = ('author',)
        verbose_name = 'Автор - подписчик'
        verbose_name_plural = verbose_name
        constraints = [
            models.UniqueConstraint(
                fields=['author', 'user'],
                name='unique_author_user'
            ),
            models.CheckConstraint(
                check=~models.Q(author=models.F('user')),
                name='author_and_user_different',
            )
        ]

    def __str__(self):
        return f"{self.author} - {self.user}"
