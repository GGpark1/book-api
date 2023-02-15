"""
Test for book APIs.
"""
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from core.models import (
    Book,
)
from book.serializers import (
    BookSerializer,
    BookDetailSerializer,
    )

BOOK_URL = reverse('book:book-list')

def create_book(**params):
    """Create and return a sample recipe."""
    defaults = {
        'title': 'Sample book',
        'price': 10000,
        'description': 'Sample book description',
    }
    defaults.update(params)

    book = Book.objects.create(**defaults)
    return book

def detail_url(book_id):
    """Create and return a book detail URL."""
    return reverse('book:book-detail', args=[book_id])

def create_superuser(**params):
    """Create and return a superuser."""
    return get_user_model().objects.create_superuser(**params)

class PublicBookApiTest(TestCase):
    """Test unauthenticated API requests."""

    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        """Test auth is required to call API."""
        res = self.client.get(BOOK_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateBookApiTest(TestCase):
    """Test authenticated API requests."""

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email='user@example.com',
            password='password',
        )
        self.superuser = create_superuser(
            email='superuser@example.com',
            password='superuser123'
        )
        self.client.force_authenticate(self.user)

    def test_retrieve_books(self):
        """Test retrieving a list of books."""

        create_book()
        create_book()

        res = self.client.get(BOOK_URL)

        books = Book.objects.all().order_by('-id')
        serializer = BookSerializer(books, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_get_book_detail(self):
        """Test get book details."""
        book = create_book()

        url = detail_url(book.id)
        res = self.client.get(url)

        serializer = BookDetailSerializer(book)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_create_book_admin(self):
        """Test creating a book by admin."""
        payload = {
            'title': 'Sample Book',
            'price': 10000,
            'description': 'Sample Description'
        }

        self.client.force_authenticate(self.superuser)
        res = self.client.post(BOOK_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        book = Book.objects.get(id=res.data['id'])
        for k, v in payload.items():
            self.assertEqual(getattr(book, k), v)

    def test_create_book_limit_to_user(self):
        """Test creating of book is limited to user."""
        payload = {
            'title': 'Sample Book',
            'price': 10000,
            'description': 'Sample Description'
        }

        res = self.client.post(BOOK_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_partial_update(self):
        """Test partial update of a book."""
        original_price = 10000
        book = create_book(
            title='original title',
            price=original_price,
            description='Sample description')

        payload = {'title': 'New Title'}
        url = detail_url(book.id)
        self.client.force_authenticate(self.superuser)
        res = self.client.patch(url, payload)

        book.refresh_from_db()
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(book.title, payload['title'])
        self.assertEqual(book.price, original_price)

    def test_full_update(self):
        """Test full update of a book."""
        book = create_book()

        payload = {
            'title': 'New book title',
            'description': 'New book Description',
            'price': 20000
        }

        self.client.force_authenticate(self.superuser)
        url = detail_url(book.id)
        res = self.client.put(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        book.refresh_from_db()
        for k, v in payload.items():
            self.assertEqual(getattr(book, k), v)

    def test_delete_book(self):
        """Test deleting a book successful."""
        book = create_book()

        self.client.force_authenticate(self.superuser)
        url = detail_url(book.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Book.objects.filter(id=book.id).exists())