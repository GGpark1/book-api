"""
Test for the Author APIs.
"""
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from core.models import (
    Author,
)
from book.serializers import (
    BookSerializer,
    AuthorSerializer,
    )

AUTHOR_URL = reverse('book:author-list')

def detail_url(author_id):
    """Create and return a author detail URL."""
    return reverse('book:author-detail', args=[author_id])

def create_user(email='user@example.com', password='password123'):
    """Create and return a user."""
    return get_user_model().objects.create_user(email=email, password=password)

class PublicAuthorApiTests(TestCase):
    """Test unauthenticated API requests."""

    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        """Test auth is required for retreving author."""
        res = self.client.get(AUTHOR_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateAuthorApiTests(TestCase):
    """Test authenticated API requests."""

    def setUp(self):
        self.client = APIClient()
        self.superuser = get_user_model().objects.create_superuser(
            email='superuser@example.com',
            password='password123',
        )
        self.client.force_authenticate(self.superuser)

    def test_retireve_author(self):
        """Test retrieving a list of authors."""
        Author.objects.create(name='Test name1', email='test1@example.com')
        Author.objects.create(name='Test name2', email='test2@example.com')

        user = create_user()
        self.client.force_authenticate(user)
        res = self.client.get(AUTHOR_URL)

        authors = Author.objects.all().order_by('-name')
        serializer = AuthorSerializer(authors, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_create_author_limited_to_user(self):
        """Test creating of authors is limited to user."""
        user = create_user()

        self.client.force_authenticate(user)
        payload = {'name': 'test name',
                   'email': 'test@example.com'}
        res = self.client.post(AUTHOR_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)
        self.assertFalse(Author.objects.filter(name=payload['name']).exists())

    def test_update_author(self):
        """Test updating a author."""
        author = Author.objects.create(name='test name',
                                       email='test@example.com',)

        payload = {'name': 'new name'}
        url = detail_url(author.id)
        res = self.client.patch(url, payload)
        author.refresh_from_db()

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(payload['name'], author.name)

    def test_update_author_limited_to_user(self):
        """Test updating a author limited to user."""
        author = Author.objects.create(name='test name',
                                       email='test@example.com',)

        payload = {'name': 'new name'}
        url = detail_url(author.id)
        user = create_user()
        self.client.force_authenticate(user)
        res = self.client.patch(url, payload)
        author.refresh_from_db()

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)
        self.assertNotEqual(payload['name'], author.name)

    def test_delete_author(self):
        """Test deleting a author."""
        author = Author.objects.create(name='test name',
                                       email='test@example.com',)
        url = detail_url(author.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Author.objects.filter(id=author.id).exists())

    def test_delete_author_limited_to_user(self):
        """Test updating a author limited to user."""
        author = Author.objects.create(name='test name',
                                       email='test@example.com',)

        url = detail_url(author.id)
        user = create_user()
        self.client.force_authenticate(user)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue(Author.objects.filter(id=author.id).exists())

    def test_create_book_with_new_authors(self):
        """Test creating a book with new authors."""
        payload = {
            'title': 'test title',
            'description': 'test description',
            'price': 10000,
            'authors': [
                {'name': 'test name1', 'email': 'test1@example.com'},
                {'name': 'test name2', 'email': 'test2@example.com'}
                        ]
        }