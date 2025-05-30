from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action
from django_filters.rest_framework import DjangoFilterBackend
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from django.db import models

from apps.library.models import Book
from apps.library.api.serializers import (
    BookSerializer,
    BookDetailSerializer,
    BookCreateSerializer,
    BookUpdateSerializer,
)
from apps.library.api.permissions import IsAdminOrReadOnly
from apps.library.api.filters import BookFilter


class BookViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing books.

    - Anonymous users: Can browse and view books (read-only)
    - Authenticated users: Can browse and view books (read-only)
    - Staff users: Full CRUD operations
    """

    queryset = Book.objects.select_related("author").all()
    filter_backends = [DjangoFilterBackend]
    filterset_class = BookFilter

    def get_permissions(self):
        """
        Instantiate and return the list of permissions that this view requires.
        """
        if self.action in ["create", "update", "partial_update", "destroy"]:
            # staff only
            permission_classes = [permissions.IsAdminUser]
        else:
            # allow read-only access for anyone
            permission_classes = [permissions.AllowAny]
        return [permission() for permission in permission_classes]

    def get_serializer_class(self):
        """Return appropriate serializer based on action."""
        if self.action == "create":
            return BookCreateSerializer
        elif self.action in ["update", "partial_update"]:
            return BookUpdateSerializer
        elif self.action == "retrieve":
            return BookDetailSerializer
        return BookSerializer

    @swagger_auto_schema(
        operation_summary="List all books",
        operation_description="Get a paginated list of all books with filtering options. Anonymous users can browse books.",
        tags=["Books"],
        manual_parameters=[
            openapi.Parameter(
                "title",
                openapi.IN_QUERY,
                description="Filter by book title (case-insensitive contains)",
                type=openapi.TYPE_STRING,
            ),
            openapi.Parameter(
                "author_name",
                openapi.IN_QUERY,
                description="Filter by author name (case-insensitive contains)",
                type=openapi.TYPE_STRING,
            ),
            openapi.Parameter(
                "language",
                openapi.IN_QUERY,
                description="Filter by book language",
                type=openapi.TYPE_STRING,
                enum=["EN", "FR", "AR", "ES", "CZ", "NL"],
            ),
            openapi.Parameter(
                "is_available",
                openapi.IN_QUERY,
                description="Filter by availability (true for available books)",
                type=openapi.TYPE_BOOLEAN,
            ),
            openapi.Parameter(
                "search",
                openapi.IN_QUERY,
                description="Search in title, author name, and description",
                type=openapi.TYPE_STRING,
            ),
        ],
        responses={200: BookSerializer(many=True)},
    )
    def list(self, request, *args, **kwargs):
        """List all books with filtering."""
        try:
            return super().list(request, *args, **kwargs)
        except Exception as e:
            return Response(
                f"List failed: {str(e)}", status=status.HTTP_400_BAD_REQUEST
            )

    @swagger_auto_schema(
        operation_summary="Get book details",
        operation_description="Retrieve detailed information about a specific book. Anonymous users can view book details.",
        tags=["Books"],
        responses={
            200: BookDetailSerializer(),
            404: openapi.Response(description="Book not found"),
        },
    )
    def retrieve(self, request, *args, **kwargs):
        """Get book details."""
        try:
            return super().retrieve(request, *args, **kwargs)
        except Exception as e:
            return Response(
                f"Retrieve failed: {str(e)}", status=status.HTTP_400_BAD_REQUEST
            )

    @swagger_auto_schema(
        operation_summary="Create a new book",
        operation_description="Create a new book (staff only). Requires an existing author_id.",
        tags=["Books - Admin"],
        request_body=BookCreateSerializer,
        responses={
            201: BookDetailSerializer(),
            400: openapi.Response(description="Bad Request - Validation errors"),
            401: openapi.Response(description="Unauthorized"),
            403: openapi.Response(description="Forbidden - Staff access required"),
        },
    )
    def create(self, request, *args, **kwargs):
        """Create a new book."""
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            book = serializer.save()
            response_serializer = BookDetailSerializer(book)
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response(
                f"Create failed: {str(e)}",
                status=status.HTTP_400_BAD_REQUEST,
            )

    @swagger_auto_schema(
        operation_summary="Update a book",
        operation_description="Update an existing book (staff only). All fields are optional for partial updates.",
        tags=["Books - Admin"],
        request_body=BookUpdateSerializer,
        responses={
            200: BookDetailSerializer(),
            400: openapi.Response(description="Bad Request - Validation errors"),
            401: openapi.Response(description="Unauthorized"),
            403: openapi.Response(description="Forbidden - Staff access required"),
            404: openapi.Response(description="Book not found"),
        },
    )
    def update(self, request, *args, **kwargs):
        """Update a book (PUT or PATCH). Always supports partial updates."""
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            book = serializer.save()
            response_serializer = BookDetailSerializer(book)
            return Response(response_serializer.data)
        except Exception as e:
            return Response(f"Update failed: {str(e)}", status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        operation_summary="Partially update a book",
        operation_description="Partially update an existing book (staff only). All fields are optional.",
        tags=["Books - Admin"],
        request_body=BookUpdateSerializer,
        responses={
            200: BookDetailSerializer(),
            400: openapi.Response(description="Bad Request - Validation errors"),
            401: openapi.Response(description="Unauthorized"),
            403: openapi.Response(description="Forbidden - Staff access required"),
            404: openapi.Response(description="Book not found"),
        },
    )
    def partial_update(self, request, *args, **kwargs):
        """Partially update a book (PATCH). All fields are optional."""
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            book = serializer.save()
            response_serializer = BookDetailSerializer(book)
            return Response(response_serializer.data)
        except Exception as e:
            return Response(
                f"Partial update failed: {str(e)}",
                status=status.HTTP_400_BAD_REQUEST,
            )

    @swagger_auto_schema(
        operation_summary="Delete a book",
        operation_description="Delete an existing book (staff only).",
        tags=["Books - Admin"],
        responses={
            204: openapi.Response(description="Book deleted successfully"),
            401: openapi.Response(description="Unauthorized"),
            403: openapi.Response(description="Forbidden - Staff access required"),
            404: openapi.Response(description="Book not found"),
        },
    )
    def destroy(self, request, *args, **kwargs):
        """Delete a book."""
        try:
            return super().destroy(request, *args, **kwargs)
        except Exception as e:
            return Response(
                f"Delete failed: {str(e)}",
                status=status.HTTP_400_BAD_REQUEST,
            )

    @action(detail=False, methods=["get"], permission_classes=[permissions.AllowAny])
    @swagger_auto_schema(
        operation_summary="List popular books",
        operation_description="Get a list of books ordered by popularity (most borrowed).",
        tags=["Books"],
        responses={200: BookSerializer(many=True)},
    )
    def popular(self, request):
        """Get most borrowed books."""
        try:
            popular_books = (
                Book.objects.select_related("author")
                .annotate(loan_count=models.Count("loans"))
                .filter(loan_count__gt=0)
                .order_by("-loan_count")[:10]
            )

            # apply the same filterset to popular books
            filterset = self.filterset_class(request.GET, queryset=popular_books)
            if filterset.is_valid():
                popular_books = filterset.qs

            serializer = self.get_serializer(popular_books, many=True)
            return Response(serializer.data)
        except Exception as e:
            return Response(
                f"Popular books failed: {str(e)}",
                status=status.HTTP_400_BAD_REQUEST,
            )
