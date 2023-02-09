"""
Test for models.
"""
from unittest.mock import patch
from django.test import TestCase
from django.contrib.auth import get_user_model
from core import models

def create_user(email='user@example.com', password='password123', **kwargs):
    """Create and retrun a new user."""
    return get_user_model.objects.create_user(email, password, **kwargs)

class ModelTests(TestCase):
    """Test models"""

    def test_create_user_with_email_successful(self):
        """Test creating a user with an email is successful."""
        email = 'test@example.com'
        password = 'password123'
        payload = {'gender': 'male',
                   'birth': 900410,}
        user = get_user_model().objects.create_user(email=email,
                                                    password=password,
                                                    **payload)

        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))