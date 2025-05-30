"""
Factory classes for creating test data for the users app.
"""

import factory
from django.contrib.auth import get_user_model
from faker import Faker

fake = Faker()
User = get_user_model()


class UserFactory(factory.django.DjangoModelFactory):
    """Factory for creating User instances."""

    class Meta:
        model = User

    email = factory.Sequence(lambda n: f"user{n}@example.com")
    username = factory.Sequence(lambda n: f"user{n}")
    first_name = factory.Faker("first_name")
    last_name = factory.Faker("last_name")
    phone_number = factory.Faker("phone_number")
    date_of_birth = factory.Faker("date_of_birth", minimum_age=18, maximum_age=80)
    is_active = True
    is_verified = False
    max_books_allowed = 5

    @factory.post_generation
    def password(self, create, extracted, **kwargs):
        """Set password after user creation."""
        password = extracted or "TestPass123!"
        self.set_password(password)
        if create:
            self.save()


class AdminUserFactory(UserFactory):
    """Factory for creating admin User instances."""

    email = factory.Sequence(lambda n: f"admin{n}@example.com")
    username = factory.Sequence(lambda n: f"admin{n}")
    is_staff = True
    is_superuser = True
    is_verified = True


class VerifiedUserFactory(UserFactory):
    """Factory for creating verified User instances."""

    is_verified = True
