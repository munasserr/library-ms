import pytest
from rest_framework import status
from rest_framework.test import APIClient
from datetime import date
from apps.library.models.loan_models import Loan
from apps.library.tests.fixtures.loan_fixtures import (
    user,
    active_loan,
    returned_loan,
    multiple_loans,
)  # noqa
from apps.library.tests.fixtures.book_fixtures import book  # noqa
from apps.library.tests.factories.loan_factories import StaffUserFactory  # noqa


@pytest.mark.django_db
class TestLoanAPI:
    BASE_URL = "/api/library/loans"

    @pytest.fixture
    def api_client(self):
        return APIClient()

    @pytest.fixture
    def staff_user(self):
        return StaffUserFactory()

    @pytest.fixture
    def authenticated_client(self, api_client, user):
        api_client.force_authenticate(user=user)
        return api_client

    @pytest.fixture
    def staff_client(self, api_client, staff_user):
        api_client.force_authenticate(user=staff_user)
        return api_client

    @pytest.mark.parametrize(
        "endpoint,method,client_type,expected_status",
        [
            ("/all-borrows/", "get", "staff", status.HTTP_200_OK),
            ("/borrows/", "get", "user", status.HTTP_200_OK),
            ("/borrow/", "post", "user", status.HTTP_201_CREATED),
            ("/return/", "post", "user", status.HTTP_200_OK),
        ],
    )
    def test_loan_endpoints_status(
        self,
        authenticated_client,
        staff_client,
        book,
        active_loan,
        endpoint,
        method,
        client_type,
        expected_status,
    ):
        url = f"{self.BASE_URL}{endpoint}"
        client = staff_client if client_type == "staff" else authenticated_client

        data = None
        if method == "post":
            if "borrow" in endpoint:
                data = {"book_id": book.id}
            elif "return" in endpoint:
                data = {"loan_id": active_loan.id}

        response = getattr(client, method)(url, data=data, format="json")
        assert response.status_code == expected_status

    @pytest.mark.parametrize(
        "filter_param,expected_min_count,client_type",
        [
            ("?status=active", 1, "staff"),
            ("?status=returned", 1, "staff"),
            ("", 1, "user"),  # No filter, should return user's loans
        ],
    )
    def test_loan_filters(
        self,
        authenticated_client,
        staff_client,
        active_loan,
        returned_loan,
        multiple_loans,
        filter_param,
        expected_min_count,
        client_type,
    ):
        endpoint = "/all-borrows/" if client_type == "staff" else "/borrows/"
        url = f"{self.BASE_URL}{endpoint}{filter_param}"
        client = staff_client if client_type == "staff" else authenticated_client

        response = client.get(url)
        assert response.status_code == status.HTTP_200_OK

    @pytest.mark.parametrize(
        "scenario,expected_status,expected_error",
        [
            (
                "borrow_unavailable",
                status.HTTP_400_BAD_REQUEST,
                "This book is currently borrowed by another user",
            ),
            (
                "return_nonexistent",
                status.HTTP_400_BAD_REQUEST,
                "Loan with this ID does not exist",
            ),
            (
                "return_already_returned",
                status.HTTP_400_BAD_REQUEST,
                "This book has already been returned",
            ),
        ],
    )
    def test_loan_error_scenarios(
        self,
        authenticated_client,
        active_loan,
        returned_loan,
        scenario,
        expected_status,
        expected_error,
    ):
        if scenario == "borrow_unavailable":
            url = f"{self.BASE_URL}/borrow/"
            data = {"book_id": active_loan.book.id}
        elif scenario == "return_nonexistent":
            url = f"{self.BASE_URL}/return/"
            data = {"loan_id": 99999}
        else:  # return_already_returned
            url = f"{self.BASE_URL}/return/"
            data = {"loan_id": returned_loan.id}

        response = authenticated_client.post(url, data=data, format="json")
        assert response.status_code == expected_status
        assert expected_error in str(response.content)

    def test_unauthorized_access(self, api_client, book, active_loan):
        """Test that unauthenticated users cannot access loan endpoints."""
        # Try to list loans
        response = api_client.get(f"{self.BASE_URL}/borrows/")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

        # Try to borrow a book
        response = api_client.post(
            f"{self.BASE_URL}/borrow/",
            data={"book_id": book.id},
            format="json",
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

        # Try to return a book
        response = api_client.post(
            f"{self.BASE_URL}/return/",
            data={"loan_id": active_loan.id},
            format="json",
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
