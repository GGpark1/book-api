"""
Tests for the genre APIs.
"""
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from core.models import (Book,
                         Author,
                         Genre)
from book.serializers import GenreSerializer

GENRE_URL = reverse('book:genre-list')

def detail_url(id):
    """Create and return a genre detail URL."""
    return reverse('book:genre-detail', args=[id])


class PublicGenreApiTests(TestCase):
    """Test unauthenticated API requests."""

    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        """Test auth required for retrieving genres."""
        res = self.client.get(GENRE_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateGenreApiTests(TestCase):
    """Test authenticate API requests."""

    def setUp(self):
        self.user = get_user_model().objects.create_superuser(
            email='superuser@example.com',
            password='testpassword',
        )
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_retrieve_genres(self):
        """Test retrieving a list of genres."""
        Genre.objects.create(name='Novel')
        Genre.objects.create(name='Comic')

        user = get_user_model().objects.create_user(
            email='test@example.com',
            password='testpassword',)
        self.client.force_authenticate(user)
        res = self.client.get(GENRE_URL)

        genres = Genre.objects.all().order_by('-name')
        serializer = GenreSerializer(genres, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_create_genre_limited_to_user(self):
        """Test creating of genre is limited to user."""
        payload = {'name': 'Novel'}

        user = get_user_model().objects.create_user(
            email='test@example.com',
            password='testpassword',)
        self.client.force_authenticate(user)
        res = self.client.post(GENRE_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)
        self.assertFalse(Genre.objects.filter(name=payload['name']).exists())

    def test_update_genre(self):
        """Test updating a genre."""
        genre = Genre.objects.create(name='Philosophics')
        payload = {'name': 'Socialscience'}

        url = detail_url(genre.id)
        res = self.client.patch(url, payload)
        genre.refresh_from_db()

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(genre.name, payload['name'])

    def test_delete_genre(self):
        """Test deleting a genre."""
        genre_name = 'Computer Science'
        genre = Genre.objects.create(name=genre_name)

        url = detail_url(genre.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Genre.objects.filter(name=genre_name).exists())

