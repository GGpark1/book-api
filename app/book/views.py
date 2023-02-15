"""
Views for the book APIs.
"""
from rest_framework import (
    viewsets,
    mixins,
    status,
)
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from core.models import Book
from core.permissions import IsAdminOrReadOnly
from book import serializers

class BookViewSet(viewsets.ModelViewSet):
    """View for manage book APIs."""
    serializer_class = serializers.BookDetailSerializer
    queryset = Book.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated, IsAdminOrReadOnly]

    def get_queryset(self):
        return self.queryset.order_by('-id')

    def get_serializer_class(self):
        """Return the serializer class for request."""
        if self.action == 'list':
            return serializers.BookSerializer

        return self.serializer_class