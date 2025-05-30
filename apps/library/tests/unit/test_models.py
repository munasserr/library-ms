import pytest
from datetime import date, timedelta
from django.core.exceptions import ValidationError
from apps.library.models.book_models import Author, Book
from apps.library.models.loan_models import Loan
from apps.library.tests.fixtures.book_fixtures import author, book  # noqa
from apps.library.tests.fixtures.loan_fixtures import (
    user,
    active_loan,
    multiple_loans,
)  # noqa


@pytest.mark.django_db
class TestAuthorModel:
    def test_author_creation(self, author):
        assert isinstance(author, Author)
        assert author.name is not None
        assert author.nationality is not None

    def test_author_age_calculation(self, author):
        author.date_of_birth = date(1990, 1, 1)
        author.save()
        assert author.age is not None

    def test_future_birth_date_validation(self, author):
        with pytest.raises(ValidationError):
            author.date_of_birth = date.today() + timedelta(days=1)
            author.save()

    def test_death_before_birth_validation(self, author):
        with pytest.raises(ValidationError):
            author.date_of_birth = date(1990, 1, 1)
            author.date_of_death = date(1989, 1, 1)
            author.save()


@pytest.mark.django_db
class TestBookModel:
    def test_book_creation(self, book):
        assert isinstance(book, Book)
        assert book.title is not None
        assert book.isbn is not None
        assert book.is_available is True

    def test_book_string_representation(self, book):
        expected = f"{book.title} - {book.author.name}"
        assert str(book) == expected

    def test_invalid_page_count(self, book):
        with pytest.raises(ValidationError):
            book.page_count = 0
            book.save()

    def test_future_publish_date(self, book):
        with pytest.raises(ValidationError):
            book.publish_date = date.today() + timedelta(days=1)
            book.save()


@pytest.mark.django_db
class TestLoanModel:
    def test_loan_creation(self, active_loan):
        assert isinstance(active_loan, Loan)
        assert active_loan.returned_at is None
        assert not active_loan.book.is_available

    def test_loan_return(self, active_loan):
        active_loan.returned_at = date.today()
        active_loan.save()
        assert active_loan.is_returned()

    def test_invalid_return_date(self, active_loan):
        with pytest.raises(ValidationError):
            active_loan.returned_at = active_loan.borrowed_at.date() - timedelta(days=1)
            active_loan.save()

    def test_multiple_active_loans(self, user, multiple_loans):
        assert len(multiple_loans) == 3
        for loan in multiple_loans:
            assert loan.user == user
            assert not loan.is_returned()
