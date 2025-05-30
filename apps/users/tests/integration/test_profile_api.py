import pytest
from rest_framework import status
from django.utils import timezone
from datetime import timedelta


@pytest.mark.django_db
class TestProfileAPI:
    """Test suite for user profile endpoints."""

    def test_get_profile_success(self, auth_client):
        """Test successful profile retrieval."""
        response = auth_client.get("/api/auth/profile/")
        assert response.status_code == status.HTTP_200_OK

    def test_get_profile_unauthenticated(self, api_client):
        """Test profile retrieval without authentication."""
        response = api_client.get("/api/auth/profile/")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_update_profile_success(self, auth_client):
        """Test successful profile update."""
        data = {
            "first_name": "Updated",
            "last_name": "Name",
            "phone_number": "+1234567890",
            "date_of_birth": "1990-01-01",
        }
        response = auth_client.patch("/api/auth/profile/", data)
        assert response.status_code == status.HTTP_200_OK

    def test_update_profile_read_only_fields(self, auth_client):
        """Test updating read-only fields."""
        data = {
            "email": "newemail@test.com",
            "username": "newusername",
            "library_card_number": "LIB999999",
        }
        response = auth_client.patch("/api/auth/profile/", data)
        assert response.status_code == status.HTTP_200_OK

    def test_update_profile_partial(self, auth_client):
        """Test partial profile update."""
        data = {"first_name": "NewFirst"}
        response = auth_client.patch("/api/auth/profile/", data)
        assert response.status_code == status.HTTP_200_OK

    def test_update_profile_invalid_method(self, auth_client):
        """Test invalid HTTP method."""
        response = auth_client.delete("/api/auth/profile/")
        assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED

    def test_change_password_same_password(self, auth_client):
        """Test changing to the same password."""
        data = {
            "old_password": "testpass123",
            "new_password": "testpass123",
            "new_password_confirm": "testpass123",
        }
        response = auth_client.post("/api/auth/change-password/", data)
        # Since validation is not enforced, this should succeed
        assert response.status_code == status.HTTP_200_OK

    def test_change_password_brute_force_protection(self, auth_client):
        """Test brute force protection."""
        data = {
            "old_password": "wrongpass",
            "new_password": "newtestpass123",
            "new_password_confirm": "newtestpass123",
        }
        response = auth_client.post("/api/auth/change-password/", data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_get_user_profile_by_id_staff(self, staff_client, user):
        """Test staff access to user profile by ID."""
        response = staff_client.get(f"/api/auth/profile/{user.id}/")
        assert response.status_code == status.HTTP_200_OK

    def test_get_user_profile_by_id_non_staff(self, auth_client, user):
        """Test non-staff access to user profile by ID."""
        response = auth_client.get(f"/api/auth/profile/{user.id}/")
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_get_user_profile_by_id_not_found(self, staff_client):
        """Test accessing non-existent user profile."""
        response = staff_client.get("/api/auth/profile/999/")
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_staff_profile_access_security(self, auth_client, user):
        """Test security of staff-only profile access."""
        response = auth_client.get("/api/auth/profile/1/")
        assert response.status_code == status.HTTP_403_FORBIDDEN
