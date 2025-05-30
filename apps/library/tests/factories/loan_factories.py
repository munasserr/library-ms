import factory
from factory.django import DjangoModelFactory
from datetime import date
from apps.library.models.loan_models import Loan
from django.contrib.auth import get_user_model
from .book_factories import BookFactory

User = get_user_model()


class UserFactory(DjangoModelFactory):
    class Meta:
        model = User

    username = factory.Sequence(lambda n: f"user_{n}")
    email = factory.LazyAttribute(lambda obj: f"{obj.username}@example.com")
    password = factory.PostGenerationMethodCall("set_password", "testpass123")
    is_active = True


class StaffUserFactory(UserFactory):
    is_staff = True


class LoanFactory(DjangoModelFactory):
    class Meta:
        model = Loan

    user = factory.SubFactory(UserFactory)
    book = factory.SubFactory(BookFactory)
    returned_at = None

    @factory.post_generation
    def mark_book_unavailable(self, create, extracted, **kwargs):
        if create and not self.returned_at:
            self.book.is_available = False
            self.book.save()
