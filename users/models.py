from django.contrib.auth.models import AbstractUser, Group, Permission
from django.db import models


class CustomUser(AbstractUser):
    username = None
    email = models.EmailField(unique=True, verbose_name='E-mail')
    birth_day = models.DateField(verbose_name='дата рождения')
    phone = models.CharField(unique=True, max_length=35, verbose_name='номер телефона')

    USERNAME_FIELD = 'email'

    REQUIRED_FIELDS = []


    class Meta:
        verbose_name = 'пациент'
        verbose_name_plural = 'пациенты'


