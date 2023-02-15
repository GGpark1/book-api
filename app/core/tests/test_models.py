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
        payload = {'gender': 0,
                   'birth': '1990-04-10',}
        user = get_user_model().objects.create_user(email=email,
                                                    password=password,
                                                    **payload)

        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))

    def test_new_user_email_normalized(self):
        """Test email is normalized for new users."""
        sample_emails = [
            ['test1@EXAMPLE.com', 'test1@example.com'],
            ['Test2@Example.com', 'Test2@example.com'],
            ['TEST3@EXAMPLE.COM', 'TEST3@example.com'],
            ['test4@example.COM', 'test4@example.com'],
        ]

        payload = {'gender': 0,
                   'birth': '1990-04-10',}

        for email, expected in sample_emails:
            user = get_user_model().objects.create_user(
                email=email,
                password='sample123',
                **payload
            )
            self.assertEqual(user.email, expected)

    def test_is_user_email_valid(self):
        """Test email format is valid"""
        sample_emails = [
            '@example.com',
            'test1@com',
            'example.com',
            'test1',
            '.com',
            '',
        ]

        payload = {'gender': 0,
                   'birth': '1990-04-10',}

        for email in sample_emails:
            with self.assertRaises(ValueError):
                get_user_model().objects.create_user(
                    email=email,
                    password='sample123',
                    **payload
                )

    def test_create_superuser(self):
        """Test create superuser."""
        user = get_user_model().objects.create_superuser(
            'test1@example.com',
            'test123',
        )

        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)

    def test_create_book(self):
        """Test creating a book is successful."""
        book = models.Book.objects.create(
            title='The Capital',
            price=3000,
            description='Description of the The capital.'
        )

        self.assertEqual(str(book), book.title)

    def test_create_author(self):
        """Test creating a author is successful."""
        author = models.Author.objects.create(
            name='John',
            email='test@example.com',
        )

