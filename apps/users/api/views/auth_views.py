from rest_framework import status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError
from django.contrib.auth import login
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from apps.users.models import CustomUser
from apps.users.api.serializers.auth_serializers import UserLoginSerializer
from apps.users.api.serializers.profile_serializers import UserProfileSerializer


class UserLoginView(APIView):
    """
    API endpoint for user authentication.

    Authenticates user credentials and returns JWT tokens.
    """

    permission_classes = [permissions.AllowAny]

    @swagger_auto_schema(
        operation_summary="User login",
        operation_description="Authenticate user and return JWT tokens",
        request_body=UserLoginSerializer,
        responses={
            200: openapi.Response(
                description="Login successful",
                examples={
                    "application/json": {
                        "message": "Login successful",
                        "user": {
                            "id": 1,
                            "email": "user@example.com",
                            "username": "username",
                            "full_name": "John Doe",
                        },
                        "tokens": {
                            "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
                            "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
                        },
                    }
                },
            ),
            400: openapi.Response(description="Invalid credentials"),
            401: openapi.Response(description="Authentication failed"),
        },
        tags=["Authentication"],
    )
    def post(self, request):
        """Handle user login."""
        serializer = UserLoginSerializer(data=request.data)

        if serializer.is_valid():
            user = serializer.validated_data["user"]

            # generate JWT tokens
            refresh = RefreshToken.for_user(user)
            access_token = refresh.access_token

            login(request, user)

            user_data = UserProfileSerializer(user).data

            response_data = {
                "message": "Login successful",
                "user": user_data,  # we can not do this or decrypt the token in client side to get the user data
                "tokens": {"access": str(access_token), "refresh": str(refresh)},
            }

            return Response(response_data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserLogoutView(APIView):
    """
    API endpoint for user logout.

    Blacklists the refresh token to invalidate the JWT session.
    """

    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="User logout",
        operation_description="Logout user by blacklisting refresh token",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "refresh_token": openapi.Schema(
                    type=openapi.TYPE_STRING, description="Refresh token to blacklist"
                )
            },
        ),
        responses={
            200: openapi.Response(description="Logout successful"),
            400: openapi.Response(description="Invalid token"),
        },
        tags=["Authentication"],
    )
    def post(self, request):
        """Handle user logout."""
        try:
            refresh_token = request.data.get("refresh_token")

            if not refresh_token:
                return Response(
                    "Refresh token is required",
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # blacklist the refresh token
            token = RefreshToken(refresh_token)
            token.blacklist()

            return Response("Logout successful", status=status.HTTP_200_OK)

        except TokenError:
            return Response("Invalid token", status=status.HTTP_400_BAD_REQUEST)
