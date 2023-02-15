"""
Serializers for book APIs.
"""
from rest_framework import serializers
from core.models import (
    Book,
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