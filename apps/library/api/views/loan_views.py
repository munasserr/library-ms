from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action
from django_filters.rest_framework import DjangoFilterBackend
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from apps.library.models import Loan, Book
from apps.library.api.serializers import (
    LoanSerializer,
    BorrowBookSerializer,
    ReturnBookSerializer,
)
from apps.library.api.filters import LoanFilter
from django.contrib.auth import get_user_model
from apps.library.api.permissions.library_permissions import IsAdminForAllLoans

User = get_user_model()


class LoanViewSet(viewsets.ViewSet):
    """
    ViewSet for borrowing and returning books, and listing borrows.
    """

    filter_backends = [DjangoFilterBackend]
    filterset_class = LoanFilter

    def get_permissions(self):
        if self.action == "all_borrows":
            return [IsAdminForAllLoans()]
        return [permissions.IsAuthenticated()]

    def get_queryset(self):
        return Loan.objects.select_related("user", "book", "book__author").all()

    @swagger_auto_schema(
        operation_summary="Borrow a book",
        operation_description="User borrows a book. Provide book_id.",
        request_body=BorrowBookSerializer,
        responses={
            201: LoanSerializer(),
            400: openapi.Response(description="Validation errors"),
            401: openapi.Response(description="Authentication required"),
        },
        tags=["Loans"],
    )
    @action(detail=False, methods=["post"], url_path="borrow")
    def borrow(self, request):
        serializer = BorrowBookSerializer(
            data=request.data, context={"request": request}
        )
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        try:
            book = Book.objects.get(id=serializer.validated_data["book_id"])
            if not book.is_available:
                return Response(
                    {"book_id": ["This book is currently borrowed by another user."]},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            loan = Loan.objects.create(user=request.user, book=book)
            book.is_available = False
            book.save(update_fields=["is_available"])
            return Response(LoanSerializer(loan).data, status=status.HTTP_201_CREATED)
        except Book.DoesNotExist:
            return Response(
                {"book_id": ["Book with this ID does not exist."]},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except Exception as e:
            return Response(
                {"detail": str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )

    @swagger_auto_schema(
        operation_summary="Return a book",
        operation_description="User returns a book. Provide loan_id.",
        request_body=ReturnBookSerializer,
        responses={
            200: LoanSerializer(),
            400: openapi.Response(description="Validation errors"),
            401: openapi.Response(description="Authentication required"),
        },
        tags=["Loans"],
    )
    @action(detail=False, methods=["post"], url_path="return")
    def return_book(self, request):
        serializer = ReturnBookSerializer(
            data=request.data, context={"request": request}
        )
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        try:
            loan = Loan.objects.get(id=serializer.validated_data["loan_id"])
            if loan.returned_at is not None:
                return Response(
                    {"loan_id": ["This book has already been returned."]},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            if not (request.user.is_staff or loan.user == request.user):
                return Response(
                    {"detail": "You can only return your own borrowed books."},
                    status=status.HTTP_403_FORBIDDEN,
                )

            loan.returned_at = loan.modified = loan.modified.now()
            loan.save()
            loan.book.is_available = True
            loan.book.save(update_fields=["is_available"])
            return Response(LoanSerializer(loan).data)
        except Loan.DoesNotExist:
            return Response(
                {"loan_id": ["Loan with this ID does not exist."]},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except Exception as e:
            return Response(
                {"detail": str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )

    @swagger_auto_schema(
        operation_summary="List your borrows",
        operation_description="List all your borrows with filters (active, inactive, book title, etc.)",
        manual_parameters=[
            openapi.Parameter(
                "status",
                openapi.IN_QUERY,
                description="active/returned",
                type=openapi.TYPE_STRING,
                enum=["active", "returned"],
            ),
            openapi.Parameter(
                "book_title",
                openapi.IN_QUERY,
                description="Filter by book title",
                type=openapi.TYPE_STRING,
            ),
        ],
        responses={200: LoanSerializer(many=True)},
        tags=["Loans"],
    )
    @action(detail=False, methods=["get"], url_path="borrows")
    def user_borrows(self, request):
        qs = self.get_queryset().filter(user=request.user)
        filterset = LoanFilter(request.GET, queryset=qs)
        if filterset.is_valid():
            qs = filterset.qs
        return Response(LoanSerializer(qs, many=True).data)

    @swagger_auto_schema(
        operation_summary="List all borrows (admin)",
        operation_description="Admin: List all borrows in the system with filters.",
        manual_parameters=[
            openapi.Parameter(
                "status",
                openapi.IN_QUERY,
                description="active/returned",
                type=openapi.TYPE_STRING,
                enum=["active", "returned"],
            ),
            openapi.Parameter(
                "book_title",
                openapi.IN_QUERY,
                description="Filter by book title",
                type=openapi.TYPE_STRING,
            ),
            openapi.Parameter(
                "user",
                openapi.IN_QUERY,
                description="Filter by username",
                type=openapi.TYPE_STRING,
            ),
        ],
        responses={200: LoanSerializer(many=True)},
        tags=["Loans - Admin"],
    )
    @action(
        detail=False,
        methods=["get"],
        url_path="all-borrows",
        permission_classes=[IsAdminForAllLoans],
    )
    def all_borrows(self, request):
        qs = self.get_queryset()
        filterset = LoanFilter(request.GET, queryset=qs)
        if filterset.is_valid():
            qs = filterset.qs
        return Response(LoanSerializer(qs, many=True).data)

    @swagger_auto_schema(
        operation_summary="List a user's borrows (admin)",
        operation_description="Admin: List all borrows for a specific user.",
        manual_parameters=[
            openapi.Parameter(
                "status",
                openapi.IN_QUERY,
                description="active/returned",
                type=openapi.TYPE_STRING,
                enum=["active", "returned"],
            ),
            openapi.Parameter(
                "book_title",
                openapi.IN_QUERY,
                description="Filter by book title",
                type=openapi.TYPE_STRING,
            ),
        ],
        responses={200: LoanSerializer(many=True)},
        tags=["Loans - Admin"],
    )
    @action(
        detail=True,
        methods=["get"],
        url_path="user-borrows",
        permission_classes=[IsAdminForAllLoans],
    )
    def user_borrows_admin(self, request, pk=None):
        try:
            user = User.objects.get(pk=pk)
        except User.DoesNotExist:
            return Response(
                {"detail": "User does not exist."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        qs = self.get_queryset().filter(user=user)
        filterset = LoanFilter(request.GET, queryset=qs)
        if filterset.is_valid():
            qs = filterset.qs
        return Response(LoanSerializer(qs, many=True).data)
