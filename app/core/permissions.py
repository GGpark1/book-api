from rest_framework import permissions

class IsAdminOrReadOnly(permissions.IsAdminUser):
    """Permission for book APIs"""

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        else:
            return bool(request.user and request.user.is_staff)