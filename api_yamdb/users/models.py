from django.contrib.auth.models import AbstractUser
from django.db import models

from api.validators import validate_username
from api_yamdb.settings import (AUTH_USERNAME_MAXLENGTH,
                                AUTH_EMAIL_MAXLENGTH,
                                AUTH_CONF_CODE_MAXLENGTH)


class User(AbstractUser):
    ROLE_USER = 'user'
    ROLE_MODERATOR = 'moderator'
    ROLE_ADMIN = 'admin'

    ROLE_CHOICES = (
        (ROLE_USER, 'Пользователь'),
        (ROLE_MODERATOR, 'Модератор'),
        (ROLE_ADMIN, 'Администратор'),
    )
    username = models.CharField(
        max_length=AUTH_USERNAME_MAXLENGTH,
        unique=True,
        validators=(validate_username,),
        error_messages={'unique': "Такой пользователь уже зарегистрирован."},
        verbose_name='Имя пользователя'
    )
    email = models.EmailField(
        max_length=AUTH_EMAIL_MAXLENGTH,
        unique=True,
        error_messages={'unique': "Такой адрес уже зарегистрирован."},
        verbose_name='Адрес электронной почты'
    )
    bio = models.TextField(
        blank=True,
        null=True,
        verbose_name='О себе'
    )
    role = models.CharField(
        max_length=max(len(role) for role, verbose in ROLE_CHOICES),
        choices=ROLE_CHOICES,
        default=ROLE_USER,
        verbose_name='Ролевая группа'
    )
    confirmation_code = models.CharField(
        max_length=AUTH_CONF_CODE_MAXLENGTH,
        blank=True,
        null=True,
        verbose_name='Код подтверждения'
    )

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ('-id',)

    @property
    def is_moderator(self):
        return self.role == self.ROLE_MODERATOR

    @property
    def is_admin(self):
        return (
            self.role == self.ROLE_ADMIN
            or self.is_superuser
            or self.is_staff
        )

    def __str__(self):
        return self.username
