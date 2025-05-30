import factory
from factory.django import DjangoModelFactory
from factory import fuzzy
from datetime import date, timedelta
from apps.users.models import CustomUser


class UserFactory(DjangoModelFactory):
    """Factory for creating test users."""

    class Meta:
        model = CustomUser

    # Use shorter sequences to stay within varchar(15) limit
    username = factory.Sequence(lambda n: f"user{n:02d}")
    email = factory.Sequence(lambda n: f"u{n:02d}@test.com")
    # Ensure first and last names are not too long
    first_name = factory.Faker("first_name")
    last_name = factory.Faker("last_name")
    # Ensure phone number is in correct format and length
    phone_number = factory.LazyFunction(
        lambda: f"+{fuzzy.FuzzyInteger(1, 999999999).fuzz()}"
    )
    date_of_birth = factory.LazyFunction(
        lambda: date.today() - timedelta(days=fuzzy.FuzzyInteger(7300, 25550).fuzz())
    )
    is_verified = True
    is_active = True
    password = factory.PostGenerationMethodCall("set_password", "testpass123")


class StaffUserFactory(UserFactory):
    """Factory for creating staff users."""

    is_staff = True
    max_books_allowed = 10
    username = factory.Sequence(lambda n: f"staff{n:02d}")
    email = factory.Sequence(lambda n: f"s{n:02d}@test.com")


class AdminUserFactory(StaffUserFactory):
    """Factory for creating admin users."""

    is_superuser = True
    max_books_allowed = 20
    username = factory.Sequence(lambda n: f"admin{n:02d}")
    email = factory.Sequence(lambda n: f"a{n:02d}@test.com")


class UnverifiedUserFactory(UserFactory):
    """Factory for creating unverified users."""

    is_verified = False
    username = factory.Sequence(lambda n: f"unver{n:02d}")
    email = factory.Sequence(lambda n: f"v{n:02d}@test.com")


class InactiveUserFactory(UserFactory):
    """Factory for creating inactive users."""

    is_active = False
    is_verified = False
    username = factory.Sequence(lambda n: f"inact{n:02d}")
    email = factory.Sequence(lambda n: f"i{n:02d}@test.com")
