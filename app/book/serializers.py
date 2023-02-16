"""
Serializers for book APIs.
"""
from rest_framework import serializers
from core.models import (
    Book,
    Author,
)

class AuthorSerializer(serializers.ModelSerializer):
    """Serializer for authors."""

    class Meta:
        model = Author
        fields = [
            'id', 'name', 'email',
        ]
        read_only_fields = ['id']

class AuthorCreateSerializer(AuthorSerializer):

    class Meta(AuthorSerializer.Meta):
        fields = AuthorSerializer.Meta.fields

    def validate_email(self, value):
            if value is not None:
                author_emails = Author.objects.filter(email=value).exists()
                if author_emails:
                    raise serializers.ValidationError("Email is already in use.")
                else:
                    return value

            return value


class BookSerializer(serializers.ModelSerializer):
    """Serializer for books."""
    authors = AuthorSerializer(many=True, required=False)

    class Meta:
        model = Book
        fields = [
            'id', 'title', 'price', 'authors'
        ]
        read_only_fields = ['id']

    def _get_or_create_authors(self, authors, book):
        """Handel getting or creating authors as needed."""
        for author in authors:
            author_obj, created = Author.objects.get_or_create(
                **author
            )
            book.authors.add(author_obj)

    def create(self, validated_data):
        """Create a book."""
        authors = validated_data.pop('authors', [])
        book = Book.objects.create(**validated_data)
        self._get_or_create_authors(authors, book)

        return book

    def update(self, instance, validated_data):
        """Update a book."""
        authors = validated_data.pop('authors', None)

        if authors is not None:
            instance.authors.clear()
            self._get_or_create_authors(authors, instance)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()

        return instance


class BookDetailSerializer(BookSerializer):
    """Serializer for book details."""

    class Meta(BookSerializer.Meta):
        fields = BookSerializer.Meta.fields + ['description']