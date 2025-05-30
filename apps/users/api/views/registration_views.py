from rest_framework import status, generics, permissions
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from apps.users.models import CustomUser
from apps.users.api.serializers.registration_serializers import (
    UserRegistrationSerializer,
)
from apps.users.api.serializers.profile_serializers import UserProfileSerializer


class UserRegistrationView(generics.CreateAPIView):
    """
    API endpoint for user registration.

    Creates a new user account and returns user data with JWT tokens.
    """

    serializer_class = UserRegistrationSerializer
    permission_classes = [permissions.AllowAny]

    @swagger_auto_schema(
        operation_summary="Register a new user",
        operation_description="Create a new user account with email verification",
        responses={
            201: openapi.Response(
                description="User created successfully",
                examples={
                    "application/json": {
                        "message": "User registered successfully",
                        "user": {
                            "id": 1,
                            "email": "user@example.com",
                            "username": "username",
                            "full_name": "John Doe",
                            "library_card_number": "LIB000001",
                        },
                        "tokens": {
                            "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
                            "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
                        },
                    }
                },
            ),
            400: openapi.Response(description="Validation errors"),
        },
        tags=["Registration"],
    )
    def post(self, request, *args, **kwargs):
        """Handle user registration."""
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()

            # generate JWT tokens
            refresh = RefreshToken.for_user(user)
            access_token = refresh.access_token

            # prepare response data
            user_data = UserProfileSerializer(user).data

            response_data = {
                "message": "User registered successfully",
                "user": user_data,
                "tokens": {"access": str(access_token), "refresh": str(refresh)},
            }

            return Response(response_data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
