from rest_framework import status, generics, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from django.contrib.auth import get_user_model
from apps.users.api.permissions.is_staff_permission import IsStaff
from apps.users.models import CustomUser
from apps.users.api.serializers.profile_serializers import (
    UserProfileSerializer,
    ChangePasswordSerializer,
)


class UserProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = get_user_model().objects.all()

    def get_object(self):
        return self.request.user

    @swagger_auto_schema(
        operation_summary="Get user profile",
        operation_description="Retrieve current user's profile information",
        responses={
            200: UserProfileSerializer,
            401: openapi.Response(description="Authentication required"),
        },
        tags=["Profile Management"],
    )
    def get(self, request, *args, **kwargs):
        """Handle profile retrieval."""
        serializer = self.get_serializer(self.get_object())
        return Response(serializer.data)

    @swagger_auto_schema(
        operation_summary="Update user profile",
        operation_description="Update current user's profile information",
        responses={
            200: UserProfileSerializer,
            400: openapi.Response(description="Validation errors"),
            401: openapi.Response(description="Authentication required"),
        },
        tags=["Profile Management"],
    )
    def patch(self, request, *args, **kwargs):
        """Handle partial profile update."""
        response = super().patch(request, *args, **kwargs)
        return response

    @swagger_auto_schema(
        operation_summary="Update user profile",
        operation_description="Update current user's profile information",
        responses={
            200: UserProfileSerializer,
            400: openapi.Response(description="Validation errors"),
            401: openapi.Response(description="Authentication required"),
        },
        tags=["Profile Management"],
    )
    def put(self, request, *args, **kwargs):
        """Handle full profile update."""
        response = super().put(request, *args, **kwargs)
        return response


class ChangePasswordView(APIView):
    """
    API endpoint for changing user password.

    Allows authenticated users to change their password.
    """

    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="Change user password",
        operation_description="Change current user's password",
        request_body=ChangePasswordSerializer,
        responses={
            200: openapi.Response(description="Password changed successfully"),
            400: openapi.Response(description="Validation errors"),
            401: openapi.Response(description="Authentication required"),
        },
        tags=["Profile Management"],
    )
    def post(self, request):
        """Handle password change."""
        serializer = ChangePasswordSerializer(
            data=request.data, context={"request": request}
        )

        if serializer.is_valid():
            serializer.save()

            return Response("Password changed successfully", status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@swagger_auto_schema(
    method="get",
    operation_summary="Get user profile by ID",
    operation_description="Retrieve user profile information by user ID (admin only)",
    responses={
        200: UserProfileSerializer,
        401: openapi.Response(description="Authentication required"),
        403: openapi.Response(description="Permission denied"),
        404: openapi.Response(description="User not found"),
    },
    tags=["Profile Management"],
)
@api_view(["GET"])
@permission_classes([permissions.IsAuthenticated, IsStaff])
def get_user_profile_by_id(request, user_id):
    """
    Get user profile by ID (admin only).

    This endpoint allows administrators to view any user's profile.
    """
    if not request.user.is_staff:
        return Response("Permission denied", status=status.HTTP_403_FORBIDDEN)

    try:
        user = CustomUser.objects.get(id=user_id)
        serializer = UserProfileSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except CustomUser.DoesNotExist:
        return Response("User not found", status=status.HTTP_404_NOT_FOUND)
