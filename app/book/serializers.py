"""
Serializers for book APIs.
"""
from rest_framework import serializers
from core.models import (
    Book,
    Author,
)

class BookSerializer(serializers.ModelSerializer):
    """Serializer for books."""

    class Meta:
        model = Book
        fields = [
            'id', 'title', 'price',
        ]
        read_only_fields = ['id']


class BookDetailSerializer(BookSerializer):
    """Serializer for book details."""

    class Meta(BookSerializer.Meta):
        fields = BookSerializer.Meta.fields + ['description']


class AuthorSerializer(serializers.ModelSerializer):
    """Serializer for authors."""

    class Meta:
        model = Author
        fields = [
            'id', 'name', 'email',
        ]
        read_only_fields = ['id']