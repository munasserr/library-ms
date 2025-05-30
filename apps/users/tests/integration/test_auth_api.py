import pytest
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken


@pytest.mark.django_db
class TestAuthAPI:
    """Test suite for authentication endpoints."""

    def test_login_success(self, api_client, user, login_data):
        """Test successful login."""
        response = api_client.post("/api/auth/login/", login_data)
        assert response.status_code == status.HTTP_200_OK
        assert "tokens" in response.data
        assert "access" in response.data["tokens"]
        assert "refresh" in response.data["tokens"]
        assert "user" in response.data
        assert response.data["user"]["email"] == user.email

    @pytest.mark.parametrize(
        "invalid_data,expected_error",
        [
            (
                {"email": "wrong@email.com", "password": "testpass123"},
                "No account found with this email address",
            ),
            (
                {"email": "", "password": "testpass123"},
                "This field may not be blank",
            ),
            (
                {"email": "user@example.com", "password": "wrongpass"},
                "Invalid password",
            ),
        ],
    )
    def test_login_failure(self, api_client, user, invalid_data, expected_error):
        """Test login failures with various invalid data combinations."""
        if "email" in invalid_data and invalid_data["email"] == "user@example.com":
            user.email = "user@example.com"
            user.save()

        response = api_client.post("/api/auth/login/", invalid_data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert expected_error in str(response.data)

    def test_login_inactive_user(self, api_client, inactive_user, login_data):
        """Test login with inactive user."""
        login_data["email"] = inactive_user.email
        response = api_client.post("/api/auth/login/", login_data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_logout_success(self, auth_client, user):
        """Test successful logout."""
        refresh = RefreshToken.for_user(user)
        response = auth_client.post(
            "/api/auth/logout/", {"refresh_token": str(refresh)}
        )
        assert response.status_code == status.HTTP_200_OK

    def test_logout_failure_no_token(self, auth_client):
        """Test logout without refresh token."""
        response = auth_client.post("/api/auth/logout/")
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_logout_failure_invalid_token(self, auth_client):
        """Test logout with invalid refresh token."""
        response = auth_client.post(
            "/api/auth/logout/", {"refresh_token": "invalid_token"}
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_logout_unauthenticated(self, api_client):
        """Test logout without authentication."""
        response = api_client.post("/api/auth/logout/", {"refresh_token": "some_token"})
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
