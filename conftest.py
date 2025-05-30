"""
Global pytest configuration and fixtures for the Library Management System.
"""

import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()


@pytest.fixture
def api_client():
    """Provide an API client for testing."""
    return APIClient()


@pytest.fixture
def user_factory():
    """Factory for creating test users."""

    def create_user(**kwargs):
        defaults = {
            "email": "test@example.com",
            "username": "testuser",
            "first_name": "Test",
            "last_name": "User",
            "password": "TestPass123!",
        }
        defaults.update(kwargs)

        password = defaults.pop("password")
        user = User(**defaults)
        user.set_password(password)
        user.save()
        return user

    return create_user


@pytest.fixture
def user(user_factory):
    """Create a test user."""
    return user_factory()


@pytest.fixture
def admin_user(user_factory):
    """Create an admin user."""
    return user_factory(
        email="admin@example.com", username="admin", is_staff=True, is_superuser=True
    )


@pytest.fixture
def authenticated_client(api_client, user):
    """Provide an authenticated API client."""
    api_client.force_authenticate(user=user)
    return api_client


@pytest.fixture
def admin_client(api_client, admin_user):
    """Provide an admin authenticated API client."""
    api_client.force_authenticate(user=admin_user)
    return api_client


@pytest.fixture
def jwt_tokens(user):
    """Generate JWT tokens for a user."""
    refresh = RefreshToken.for_user(user)
    return {"access": str(refresh.access_token), "refresh": str(refresh)}


@pytest.fixture
def valid_user_data():
    """Provide valid user registration data."""
    return {
        "email": "newuser@example.com",
        "username": "newuser",
        "first_name": "New",
        "last_name": "User",
        "password": "NewPass123!",
        "password_confirm": "NewPass123!",
        "phone_number": "+1234567890",
        "date_of_birth": "1990-01-01",
    }


@pytest.fixture
def invalid_user_data():
    """Provide invalid user registration data for testing validation."""
    return {
        "email": "invalid-email",
        "username": "",
        "first_name": "",
        "last_name": "",
        "password": "123",  # too weak
        "password_confirm": "456",  # doesn't match
    }
