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
    Author,
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
        self.client.force_authenticate(self.superuser)

    def test_retrieve_books(self):
        """Test retrieving a list of books."""

        create_book()
        create_book()

        self.client.force_authenticate(self.user)
        res = self.client.get(BOOK_URL)

        books = Book.objects.all().order_by('-id')
        serializer = BookSerializer(books, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_get_book_detail(self):
        """Test get book details."""
        book = create_book()

        url = detail_url(book.id)
        self.client.force_authenticate(self.user)
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

        self.client.force_authenticate(self.user)
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

        url = detail_url(book.id)
        res = self.client.put(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        book.refresh_from_db()
        for k, v in payload.items():
            self.assertEqual(getattr(book, k), v)

    def test_delete_book(self):
        """Test deleting a book successful."""
        book = create_book()

        url = detail_url(book.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Book.objects.filter(id=book.id).exists())

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
        res = self.client.post(BOOK_URL, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        books = Book.objects.filter(title=payload['title'])
        self.assertEqual(books.count(), 1)
        book = books[0]
        self.assertEqual(book.authors.count(), 2)
        for author in payload['authors']:
            exists = book.authors.filter(
                name=author['name'],
                email=author['email']
            ).exists()
            self.assertTrue(exists)

    def test_create_author_on_update(self):
        """Test creating authors when updating a book."""
        book = create_book()

        payload = {
            'authors': [
                {'name': 'test name',
                 'email': 'author@example.com'}
                ]
            }
        url = detail_url(book.id)
        res = self.client.patch(url, payload, format='json')
        book.refresh_from_db()

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        new_author = Author.objects.get(name='test name',
                                        email='author@example.com')
        self.assertIn(new_author, book.authors.all())

    def test_update_book_assign_author(self):
        """Test assigning an existing author when updating a book."""
        first_author = Author.objects.create(
            name='test name1',
            email='test1@example.com',
        )
        book = create_book()
        book.authors.add(first_author)

        second_author = Author.objects.create(
            name='test name2',
            email='test2@example.com'
        )
        payload = {
            'authors':
                [
                    {'name': 'test name2',
                     'email': 'test2@example.com',}
                    ]
        }
        url = detail_url(book.id)
        res = self.client.patch(url, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn(second_author, book.authors.all())
        self.assertNotIn(first_author, book.authors.all())

    def test_clear_book_authors(self):
        """Test clearing a book tags"""
        author = Author.objects.create(name='test name1',
                                       email='test1@example.com')
        book = create_book()
        book.authors.add(author)

        payload = {'authors': []}
        url = detail_url(book.id)
        res = self.client.patch(url, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(book.authors.count(), 0)

    def test_create_book_with_new_genre(self):
        """Test creating a book with new book."""