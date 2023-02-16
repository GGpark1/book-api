"""
Database models.
"""
import re

from django.db import models
from django.conf import settings
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)

class UserManager(BaseUserManager):

    def create_user(self, email, password=None, **kwargs):
        """Create, save and return a new user."""

        p = re.compile('^[a-zA-Z0-9+-_.]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$') # noqa

        if not p.match(email):
            raise ValueError('Check your email is valid.')

        user = self.model(email=self.normalize_email(email), **kwargs)
        user.set_password(password)
        user.save(using=self.db)

        return user

    def create_superuser(self, email, password):
        """Create a new superuser."""
        user = self.create_user(email, password)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self.db)

        return user

class User(AbstractBaseUser, PermissionsMixin):
    """USer in the system."""

    class Gender(models.IntegerChoices):
        NONE = 0
        MALE = 1
        FEMALE = 2

    email = models.EmailField(max_length=255, unique=True)
    name = models.CharField(max_length=255)
    gender = models.IntegerField(choices=Gender.choices, null=False, default=0)
    birth = models.DateField(null=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = 'email'


class Book(models.Model):
    """Book object."""
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    price = models.IntegerField(null=False)
    authors = models.ManyToManyField('Author')

    def __str__(self):
        return self.title


class Author(models.Model):
    """Author object."""
    name = models.CharField(max_length=255)
    email = models.EmailField(max_length=255)

    def __str__(self):
        return self.name