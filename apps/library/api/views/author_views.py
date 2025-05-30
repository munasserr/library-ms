from rest_framework import viewsets, permissions
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework import status

from apps.library.models import Author
from apps.library.api.serializers import (
    AuthorSerializer,
    AuthorCreateUpdateSerializer,
)


class AuthorViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing authors.

    Only staff users can perform CRUD operations on authors.
    """

    queryset = Author.objects.all()
    permission_classes = [permissions.IsAdminUser]

    def get_serializer_class(self):
        """Return appropriate serializer based on action."""
        if self.action in ["create", "update", "partial_update"]:
            return AuthorCreateUpdateSerializer
        return AuthorSerializer

    @swagger_auto_schema(
        operation_summary="List all authors",
        operation_description="List all authors (staff only)",
        tags=["Authors - Admin"],
        responses={
            200: AuthorSerializer(many=True),
            401: openapi.Response(description="Unauthorized"),
            403: openapi.Response(description="Forbidden - Staff access required"),
        },
    )
    def list(self, request, *args, **kwargs):
        try:
            return super().list(request, *args, **kwargs)
        except Exception as e:
            return Response(
                f"List failed: {str(e)}", status=status.HTTP_400_BAD_REQUEST
            )

    @swagger_auto_schema(
        operation_summary="Get author details",
        operation_description="Get author details (staff only)",
        tags=["Authors - Admin"],
        responses={
            200: AuthorSerializer(),
            401: openapi.Response(description="Unauthorized"),
            403: openapi.Response(description="Forbidden - Staff access required"),
            404: openapi.Response(description="Author not found"),
        },
    )
    def retrieve(self, request, *args, **kwargs):
        try:
            return super().retrieve(request, *args, **kwargs)
        except Exception as e:
            return Response(
                f"Retrieve failed: {str(e)}",
                status=status.HTTP_400_BAD_REQUEST,
            )

    @swagger_auto_schema(
        operation_summary="Create a new author",
        operation_description="Create a new author (staff only)",
        tags=["Authors - Admin"],
        request_body=AuthorCreateUpdateSerializer,
        responses={
            201: AuthorSerializer(),
            400: openapi.Response(description="Bad Request - Validation errors"),
            401: openapi.Response(description="Unauthorized"),
            403: openapi.Response(description="Forbidden - Staff access required"),
        },
    )
    def create(self, request, *args, **kwargs):
        try:
            return super().create(request, *args, **kwargs)
        except Exception as e:
            return Response(
                f"Create failed: {str(e)}",
                status=status.HTTP_400_BAD_REQUEST,
            )

    @swagger_auto_schema(
        operation_summary="Update an author",
        operation_description="Update an author (staff only)",
        tags=["Authors - Admin"],
        request_body=AuthorCreateUpdateSerializer,
        responses={
            200: AuthorSerializer(),
            400: openapi.Response(description="Bad Request - Validation errors"),
            401: openapi.Response(description="Unauthorized"),
            403: openapi.Response(description="Forbidden - Staff access required"),
            404: openapi.Response(description="Author not found"),
        },
    )
    def update(self, request, *args, **kwargs):
        try:
            return super().update(request, *args, **kwargs)
        except Exception as e:
            return Response(
                f"Update failed: {str(e)}",
                status=status.HTTP_400_BAD_REQUEST,
            )

    @swagger_auto_schema(
        operation_summary="Partially update an author",
        operation_description="Partially update an author (staff only)",
        tags=["Authors - Admin"],
        request_body=AuthorCreateUpdateSerializer,
        responses={
            200: AuthorSerializer(),
            400: openapi.Response(description="Bad Request - Validation errors"),
            401: openapi.Response(description="Unauthorized"),
            403: openapi.Response(description="Forbidden - Staff access required"),
            404: openapi.Response(description="Author not found"),
        },
    )
    def partial_update(self, request, *args, **kwargs):
        try:
            return super().partial_update(request, *args, **kwargs)
        except Exception as e:
            return Response(
                f"Partial update failed: {str(e)}",
                status=status.HTTP_400_BAD_REQUEST,
            )

    @swagger_auto_schema(
        operation_summary="Delete an author",
        operation_description="Delete an author (staff only)",
        tags=["Authors - Admin"],
        responses={
            204: openapi.Response(description="Author deleted successfully"),
            401: openapi.Response(description="Unauthorized"),
            403: openapi.Response(description="Forbidden - Staff access required"),
            404: openapi.Response(description="Author not found"),
        },
    )
    def destroy(self, request, *args, **kwargs):
        try:
            return super().destroy(request, *args, **kwargs)
        except Exception as e:
            return Response(
                f"Delete failed: {str(e)}",
                status=status.HTTP_400_BAD_REQUEST,
            )
