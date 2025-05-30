import pytest
from apps.users.tests.factories.user_factories import (
    UserFactory,
    StaffUserFactory,
    AdminUserFactory,
    UnverifiedUserFactory,
    InactiveUserFactory,
)


@pytest.fixture
def user():
    """Create a regular user."""
    return UserFactory()


@pytest.fixture
def another_user():
    """Create another regular user."""
    return UserFactory()


@pytest.fixture
def staff_user():
    """Create a staff user."""
    return StaffUserFactory()


@pytest.fixture
def admin_user():
    """Create an admin user."""
    return AdminUserFactory()


@pytest.fixture
def unverified_user():
    """Create an unverified user."""
    return UnverifiedUserFactory()


@pytest.fixture
def inactive_user():
    """Create an inactive user."""
    return InactiveUserFactory()


@pytest.fixture
def user_data():
    """Return valid user registration data."""
    return {
        "email": "new@test.com",
        "username": "newuser01",
        "password": "testpass123",
        "password_confirm": "testpass123",
        "first_name": "New",
        "last_name": "User",
        "phone_number": "+1234567890",
        "date_of_birth": "1990-01-01",
    }


@pytest.fixture
def login_data(user):
    """Return valid login data for a user."""
    return {
        "email": user.email,
        "password": "testpass123",
    }


@pytest.fixture
def auth_client(api_client, user):
    """Return an authenticated API client."""
    api_client.force_authenticate(user=user)
    return api_client


@pytest.fixture
def staff_client(api_client, staff_user):
    """Return an authenticated API client for staff user."""
    api_client.force_authenticate(user=staff_user)
    return api_client


@pytest.fixture
def admin_client(api_client, admin_user):
    """Return an authenticated API client for admin user."""
    api_client.force_authenticate(user=admin_user)
    return api_client
