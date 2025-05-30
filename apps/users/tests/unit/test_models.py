import pytest
from datetime import date, timedelta
from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.contrib.auth.password_validation import validate_password
from django.db.utils import DataError
from apps.users.models import CustomUser


@pytest.mark.django_db
class TestCustomUser:
    def test_user_creation(self, user):
        """Test basic user creation."""
        assert isinstance(user, CustomUser)
        assert user.email
        assert user.username
        assert user.is_active
        assert user.is_verified
        assert not user.is_staff
        assert not user.is_superuser

    def test_staff_user_creation(self, staff_user):
        """Test staff user creation."""
        assert staff_user.is_staff
        assert staff_user.max_books_allowed == 10
        assert not staff_user.is_superuser

    def test_admin_user_creation(self, admin_user):
        """Test admin user creation."""
        assert admin_user.is_staff
        assert admin_user.is_superuser
        assert admin_user.max_books_allowed == 20

    def test_unverified_user_creation(self, unverified_user):
        """Test unverified user creation."""
        assert not unverified_user.is_verified
        assert unverified_user.is_active

    def test_inactive_user_creation(self, inactive_user):
        """Test inactive user creation."""
        assert not inactive_user.is_active
        assert not inactive_user.is_verified

    def test_get_full_name(self, user):
        """Test get_full_name method."""
        assert user.get_full_name() == f"{user.first_name} {user.last_name}"

        # Test with no first/last name
        user.first_name = ""
        user.last_name = ""
        assert user.get_full_name() == user.username

    def test_get_short_name(self, user):
        """Test get_short_name method."""
        assert user.get_short_name() == user.first_name

        # Test with no first name
        user.first_name = ""
        assert user.get_short_name() == user.username

    def test_library_card_number_generation(self, user):
        """Test library card number is generated correctly."""
        assert user.library_card_number
        assert user.library_card_number.startswith("LIB")
        assert len(user.library_card_number) == 9  # LIB + 6 digits

    def test_can_borrow_books(self, user):
        """Test can_borrow_books method."""
        assert user.can_borrow_books()
        assert user.current_loans_count == 0

    @pytest.mark.parametrize(
        "phone_number,is_valid",
        [
            ("+1234567890", True),
            ("1234567890", True),
            ("123-456-7890", False),
            ("abc", False),
            ("", True),  # Optional field
            (None, True),  # Optional field
        ],
    )
    def test_phone_number_validation(self, user, phone_number, is_valid):
        """Test phone number validation."""
        user.phone_number = phone_number
        if is_valid:
            user.full_clean()  # Should not raise ValidationError
        else:
            with pytest.raises(ValidationError):
                user.full_clean()

    @pytest.mark.parametrize(
        "date_of_birth,is_valid",
        [
            (date.today() - timedelta(days=7300), True),  # 20 years ago
            (date.today() + timedelta(days=1), False),  # Future date
            (None, True),  # Optional field
        ],
    )
    def test_date_of_birth_validation(self, user, date_of_birth, is_valid):
        """Test date of birth validation."""
        user.date_of_birth = date_of_birth
        if is_valid:
            user.full_clean()  # Should not raise ValidationError
        else:
            with pytest.raises(ValidationError):
                user.full_clean()

    def test_email_uniqueness(self, user, another_user):
        """Test email uniqueness constraint."""
        another_user.email = user.email
        with pytest.raises(ValidationError):
            another_user.full_clean()

    def test_username_uniqueness(self, user, another_user):
        """Test username uniqueness constraint."""
        another_user.username = user.username
        with pytest.raises(ValidationError):
            another_user.full_clean()

    def test_library_card_number_uniqueness(self, user, another_user):
        """Test library card number uniqueness constraint."""
        another_user.library_card_number = user.library_card_number
        with pytest.raises(ValidationError):
            another_user.full_clean()

    def test_user_str_representation(self, user):
        """Test string representation of user model."""
        expected = f"{user.get_full_name()} ({user.email})"
        assert str(user) == expected

    def test_password_validation(self):
        """Test password validation rules."""
        invalid_passwords = [
            "short",  # Too short
            "12345678",  # Only numbers
            "password",  # Common password
            "abcdefgh",  # Too simple
        ]

        for invalid_password in invalid_passwords:
            with pytest.raises(ValidationError):
                validate_password(invalid_password)

    def test_date_of_birth_validation(self):
        """Test date of birth validation."""
        future_date = date.today() + timedelta(days=1)

        user = CustomUser.objects.create(
            username="testuser",
            email="test@example.com",
            first_name="Test",
            last_name="User",
            date_of_birth=future_date,
        )
        user.set_password("testpass123")

        with pytest.raises(ValidationError):
            from django.core.validators import BaseValidator

            class FutureDateValidator(BaseValidator):
                def compare(self, value, threshold):
                    return value > threshold

                def clean(self, x):
                    return x

            validator = FutureDateValidator(
                limit_value=date.today(), message="Future date not allowed"
            )
            validator(user.date_of_birth)

    def test_library_card_number_format(self, user):
        """Test library card number format."""
        assert user.library_card_number.startswith("LIB")
        assert len(user.library_card_number) == 9
        assert user.library_card_number[3:].isdigit()

    def test_max_books_allowed_validation(self):
        """Test max_books_allowed validation."""
        with pytest.raises(ValidationError):
            user = CustomUser(
                username="testuser",
                email="test@example.com",
                password="testpass123",
                max_books_allowed=-1,  # Invalid negative value
            )
            user.full_clean()

    def test_phone_number_validation(self):
        """Test phone number validation."""
        invalid_phone_numbers = [
            "123-456-7890",  # Invalid format
            "abcdefghijk",  # Non-numeric
            "+1234",  # Too short
            "+123456789012345678",  # Too long
        ]

        for invalid_phone in invalid_phone_numbers:
            user = CustomUser(
                username="testuser",
                email="test@example.com",
                password="testpass123",
                first_name="Test",
                last_name="User",
                phone_number=invalid_phone,
            )
            with pytest.raises(ValidationError):
                user.full_clean()

    def test_user_permissions(self, user, staff_user, admin_user):
        """Test user permission levels."""
        # Regular user
        assert not user.is_staff
        assert not user.is_superuser
        assert user.max_books_allowed == 5

        # Staff user
        assert staff_user.is_staff
        assert not staff_user.is_superuser
        assert staff_user.max_books_allowed == 10

        # Admin user
        assert admin_user.is_staff
        assert admin_user.is_superuser
        assert admin_user.max_books_allowed == 20
