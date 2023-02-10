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

class User(AbstractBaseUser, PermissionsMixin):
    """USer in the system."""

    class Gender(models.IntegerChoices):
        NONE = 0
        MALE = 1
        FEMALE = 2

    email = models.EmailField(max_length=255, unique=True)
    name = models.CharField(max_length=255)
    gender = models.IntegerField(choices=Gender.choices)
    birth = models.DateField(null=False)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = 'email'