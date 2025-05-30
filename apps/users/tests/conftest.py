import pytest
from rest_framework.test import APIClient

# Import all fixtures
from apps.users.tests.fixtures.user_fixtures import (  # noqa
    user,
    another_user,
    staff_user,
    admin_user,
    unverified_user,
    inactive_user,
    user_data,
    login_data,
    auth_client,
    staff_client,
    admin_client,
)


@pytest.fixture
def api_client():
    """Return an API client."""
    return APIClient()
