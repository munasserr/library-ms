from rest_framework import permissions


class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Custom permission to allow read-only access to any user,
    but only allow write permissions to admin users.
    """

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return bool(request.user and request.user.is_staff)


class IsAuthenticatedForLoans(permissions.BasePermission):
    """
    Custom permission that requires authentication for all loan operations.
    """

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated)


class IsAdminForAllLoans(permissions.BasePermission):
    """
    Custom permission that only allows admin users to view all loans.
    """

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_staff)


class IsOwnerOfLoan(permissions.BasePermission):
    """
    Custom permission to allow users to access only their own loans.
    Admins can access any loan.
    """

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        return obj.user == request.user or request.user.is_staff
