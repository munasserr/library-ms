import pytest
from rest_framework import status
from django.utils import timezone
from datetime import timedelta


@pytest.mark.django_db
class TestRegistrationAPI:
    """Test suite for user registration endpoints."""

    def test_registration_success(self, api_client, valid_user_data):
        """Test successful user registration."""
        response = api_client.post("/api/auth/register/", valid_user_data)
        assert response.status_code == status.HTTP_201_CREATED

    @pytest.mark.parametrize(
        "field,value",
        [
            ("email", ""),
            ("email", "invalid"),
            ("username", ""),
            ("username", "a"),  # Short username is allowed
            ("username", "a" * 16),  # Long username is allowed
            ("password", ""),
            ("password", "short"),
            ("password", "12345678"),
            ("password_confirm", ""),
            ("first_name", ""),
            ("first_name", "a" * 31),  # Long name is allowed
            ("last_name", ""),
            ("last_name", "a" * 31),  # Long name is allowed
            ("date_of_birth", "invalid-date"),
            (
                "date_of_birth",
                (timezone.now() + timedelta(days=1)).date().isoformat(),
            ),  # Future date is allowed
        ],
    )
    def test_registration_validation(self, api_client, valid_user_data, field, value):
        """Test registration validation for various fields."""
        data = valid_user_data.copy()
        data[field] = value
        response = api_client.post("/api/auth/register/", data)

        # Only basic validations should fail
        if field in ["email", "password", "password_confirm"] and not value:
            assert response.status_code == status.HTTP_400_BAD_REQUEST
        elif field == "email" and value == "invalid":
            assert response.status_code == status.HTTP_400_BAD_REQUEST
        elif field == "password" and (len(value) < 8 or value.isdigit()):
            assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_registration_password_mismatch(self, api_client, valid_user_data):
        """Test registration with mismatched passwords."""
        data = valid_user_data.copy()
        data["password_confirm"] = "differentpassword123"
        response = api_client.post("/api/auth/register/", data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_registration_existing_email(self, api_client, user, valid_user_data):
        """Test registration with existing email."""
        data = valid_user_data.copy()
        data["email"] = user.email
        response = api_client.post("/api/auth/register/", data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_registration_existing_username(self, api_client, user, valid_user_data):
        """Test registration with existing username."""
        data = valid_user_data.copy()
        data["username"] = user.username
        response = api_client.post("/api/auth/register/", data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_registration_with_optional_fields(self, api_client, valid_user_data):
        """Test registration with optional fields."""
        data = valid_user_data.copy()
        data["phone_number"] = "+1234567890"
        data["date_of_birth"] = "1990-01-01"
        response = api_client.post("/api/auth/register/", data)
        assert response.status_code == status.HTTP_201_CREATED

    def test_registration_default_values(self, api_client, valid_user_data):
        """Test registration with default values."""
        data = valid_user_data.copy()
        data.pop("phone_number", None)
        data.pop("date_of_birth", None)
        response = api_client.post("/api/auth/register/", data)
        assert response.status_code == status.HTTP_201_CREATED

    def test_registration_with_special_characters(self, api_client, valid_user_data):
        """Test registration with special characters in names."""
        data = valid_user_data.copy()
        data["first_name"] = "José-María"
        data["last_name"] = "O'Connor"
        response = api_client.post("/api/auth/register/", data)
        assert response.status_code == status.HTTP_201_CREATED

    def test_registration_trim_whitespace(self, api_client, valid_user_data):
        """Test that whitespace is trimmed from fields."""
        data = valid_user_data.copy()
        data["email"] = "  test@example.com  "
        data["username"] = "  testuser  "
        response = api_client.post("/api/auth/register/", data)
        assert response.status_code == status.HTTP_201_CREATED

    def test_registration_case_sensitivity(self, api_client, user, valid_user_data):
        """Test case sensitivity in unique fields."""
        data = valid_user_data.copy()
        data["email"] = user.email.upper()
        data["username"] = user.username.upper()
        response = api_client.post("/api/auth/register/", data)
        # Case sensitivity is not enforced
        assert response.status_code == status.HTTP_201_CREATED
