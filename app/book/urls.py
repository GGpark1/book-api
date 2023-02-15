"""
URL mappings for the recipe app
"""
from django.urls import (
    path,
    include,
)

from rest_framework.routers import DefaultRouter
from book import views

router = DefaultRouter()
router.register(r'books', views.BookViewSet)

app_name = 'book'

urlpatterns = [
    path('', include(router.urls)),
]
