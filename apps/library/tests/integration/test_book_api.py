import pytest
from rest_framework import status
from rest_framework.test import APIClient
from apps.library.models.book_models import Book
from apps.library.tests.fixtures.book_fixtures import (
    author,
    authors,
    book,
    books,
)  # noqa
from apps.library.tests.factories.loan_factories import StaffUserFactory  # noqa
from datetime import date, timedelta


@pytest.mark.django_db
class TestBookAPI:
    BASE_URL = "/api/library"

    @pytest.fixture
    def api_client(self):
        return APIClient()

    @pytest.fixture
    def staff_user(self):
        return StaffUserFactory()

    @pytest.fixture
    def authenticated_client(self, api_client, staff_user):
        api_client.force_authenticate(user=staff_user)
        return api_client

    @pytest.mark.parametrize(
        "endpoint,method,expected_status",
        [
            ("/books/", "get", status.HTTP_200_OK),
            ("/books/", "post", status.HTTP_201_CREATED),
            ("/books/{id}/", "get", status.HTTP_200_OK),
            ("/books/{id}/", "patch", status.HTTP_200_OK),
            ("/books/{id}/", "delete", status.HTTP_204_NO_CONTENT),
        ],
    )
    def test_book_endpoints_status(
        self, authenticated_client, book, endpoint, method, expected_status
    ):
        url = f"{self.BASE_URL}{endpoint}"
        if "{id}" in endpoint:
            url = url.replace("{id}", str(book.id))

        data = None
        if method == "post":
            data = {
                "title": "New Test Book",
                "author_id": book.author.id,
                "description": "Test description",
                "isbn": "9783161484100",
                "publish_date": (date.today() - timedelta(days=10)).isoformat(),
                "page_count": 200,
                "language": "EN",
                "is_available": True,
            }
        elif method == "patch":
            data = {
                "title": "Updated Title",
                "description": "Updated description",
                "isbn": book.isbn,
                "publish_date": book.publish_date.isoformat(),
                "page_count": book.page_count,
                "language": book.language,
                "is_available": book.is_available,
            }

        response = getattr(authenticated_client, method)(url, data=data, format="json")
        assert response.status_code == expected_status

        if method == "post":
            assert Book.objects.filter(title="New Test Book").exists()
        elif method == "patch":
            book.refresh_from_db()
            assert book.title == "Updated Title"
        elif method == "delete":
            assert not Book.objects.filter(id=book.id).exists()

    @pytest.mark.parametrize(
        "search_param,expected_min_count",
        [
            ("?search={title}", 1),  # Search by title
            ("?language=EN", 1),  # Filter by language
            ("?is_available=true", 1),  # Filter by availability
        ],
    )
    def test_book_search_and_filters(
        self, authenticated_client, book, search_param, expected_min_count
    ):
        url = f"{self.BASE_URL}/books/{search_param}"
        if "{title}" in search_param:
            url = url.replace("{title}", book.title[:10])

        response = authenticated_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) >= expected_min_count

    @pytest.mark.parametrize(
        "invalid_data,expected_error",
        [
            (
                {
                    "title": "",
                    "author_id": 1,
                    "isbn": "invalid_isbn",
                    "publish_date": date.today().isoformat(),
                    "page_count": 200,
                    "language": "EN",
                },
                "This field may not be blank",  # Django's default message for blank CharField
            ),
            (
                {
                    "title": "Test Book",
                    "author_id": 999999,  # Non-existent author
                    "isbn": "9783161484100",
                    "publish_date": date.today().isoformat(),
                    "page_count": 200,
                    "language": "EN",
                },
                "Author with this ID does not exist",
            ),
            (
                {
                    "title": "Test Book",
                    "author_id": 1,
                    "isbn": "invalid_isbn",
                    "publish_date": date.today().isoformat(),
                    "page_count": 200,
                    "language": "EN",
                },
                "ISBN must be 10 or 13 digits",
            ),
        ],
    )
    def test_book_creation_validation(
        self, authenticated_client, author, invalid_data, expected_error
    ):
        url = f"{self.BASE_URL}/books/"
        if "author_id" in invalid_data and invalid_data["author_id"] == 1:
            invalid_data["author_id"] = author.id

        response = authenticated_client.post(url, data=invalid_data, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert expected_error in str(response.content)

    def test_unauthenticated_access(self, api_client, book):
        """Test that unauthenticated users can only read books."""
        # List books - should work
        response = api_client.get(f"{self.BASE_URL}/books/")
        assert response.status_code == status.HTTP_200_OK

        # Get single book - should work
        response = api_client.get(f"{self.BASE_URL}/books/{book.id}/")
        assert response.status_code == status.HTTP_200_OK

        # Create book - should fail
        data = {
            "title": "New Book",
            "author_id": book.author.id,
            "description": "Test",
            "isbn": "9783161484100",
            "publish_date": date.today().isoformat(),
            "page_count": 200,
            "language": "EN",
        }
        response = api_client.post(f"{self.BASE_URL}/books/", data=data, format="json")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

        # Update book - should fail
        response = api_client.patch(
            f"{self.BASE_URL}/books/{book.id}/",
            data={"title": "Updated"},
            format="json",
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

        # Delete book - should fail
        response = api_client.delete(f"{self.BASE_URL}/books/{book.id}/")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
