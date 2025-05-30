import pytest
from apps.library.tests.factories.book_factories import AuthorFactory, BookFactory


@pytest.fixture
def author():
    return AuthorFactory()


@pytest.fixture
def authors():
    return [AuthorFactory() for _ in range(3)]


@pytest.fixture
def book():
    return BookFactory()


@pytest.fixture
def books():
    return [BookFactory() for _ in range(3)]


@pytest.fixture
def book_with_specific_author(author):
    return BookFactory(author=author)
