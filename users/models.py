# -*- encoding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib.auth.models import AbstractUser
from django.contrib.auth.validators import UnicodeUsernameValidator, ASCIIUsernameValidator
from django.db import models
from django.utils import six


class Rol(models.Model):
    rol = models.CharField(max_length=90, default='')

    class Meta:
        verbose_name = 'Rol'
        verbose_name_plural = 'Roles'

    def __str__(self):
        return self.rol


class User(AbstractUser):
    user_rol = models.ForeignKey(Rol, blank=True, null=True)

    class Meta(AbstractUser.Meta):
        swappable = 'AUTH_USER_MODEL'


class CustomerProfile(models.Model):
    username_validator = UnicodeUsernameValidator() if six.PY3 else ASCIIUsernameValidator()

    user = models.CharField(
        max_length=150,
        unique=True,
        validators=[username_validator],
        error_messages={
            'unique': "Ya existe un usuario con este nickname",
            'invalid': 'Máximo 50 caracteres. Letras, números y @/./+/-/_ únicamente.',
        },
    )
    phone_number = models.CharField(
        max_length=13,
        unique=True,
        error_messages={
            'unique': "Este número ya está registrado",
        },
    )
    email = models.EmailField(
        unique=True,
        error_messages={
            'unique': "Ya existe un usuario con este email",
        },
    )
    address = models.CharField(
        max_length=255,
        error_messages={
            'unique': "Ya existe un usuario con este email",
        },
    )
    longitude = models.CharField(default='0.0', max_length=30, blank=True)
    latitude = models.CharField(default=0.0, max_length=30, blank=True)
    first_dabba = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'Perfil de Usuario'
        verbose_name_plural = 'Perfiles de Usuarios'
