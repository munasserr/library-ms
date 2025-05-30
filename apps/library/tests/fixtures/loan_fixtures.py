import pytest
from datetime import date
from apps.library.tests.factories.loan_factories import UserFactory, LoanFactory
from apps.library.tests.factories.book_factories import BookFactory


@pytest.fixture
def user():
    return UserFactory()


@pytest.fixture
def users():
    return [UserFactory() for _ in range(3)]


@pytest.fixture
def active_loan(user, book):
    return LoanFactory(user=user, book=book)


@pytest.fixture
def returned_loan(user, book):
    return LoanFactory(user=user, book=book, returned_at=date.today())


@pytest.fixture
def multiple_loans(user):
    books = [BookFactory() for _ in range(3)]
    return [LoanFactory(user=user, book=book) for book in books]
