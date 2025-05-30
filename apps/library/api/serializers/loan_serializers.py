from rest_framework import serializers
from django.utils import timezone
from apps.library.models import Loan, Book


class LoanSerializer(serializers.ModelSerializer):
    """
    Serializer for Loan model - used for displaying loan information.
    """

    book_title = serializers.CharField(source="book.title", read_only=True)
    book_author = serializers.CharField(source="book.author.name", read_only=True)
    borrower_name = serializers.CharField(source="user.get_full_name", read_only=True)
    borrower_email = serializers.CharField(source="user.email", read_only=True)
    borrowed_date = serializers.DateTimeField(source="created", read_only=True)
    is_active = serializers.SerializerMethodField()

    class Meta:
        model = Loan
        fields = [
            "id",
            "book_title",
            "book_author",
            "borrower_name",
            "borrower_email",
            "borrowed_date",
            "returned_at",
            "is_active",
        ]

    def get_is_active(self, obj):
        """Check if loan is currently active."""
        return not obj.is_returned()


class BorrowBookSerializer(serializers.Serializer):
    """
    Serializer for borrowing a book.
    """

    book_id = serializers.IntegerField()

    def validate_book_id(self, value):
        """Validate that book exists and is available."""
        try:
            book = Book.objects.get(id=value)
        except Book.DoesNotExist:
            raise serializers.ValidationError("Book with this ID does not exist.")

        # check if book is already borrowed
        active_loan = book.loans.filter(returned_at__isnull=True).first()
        if active_loan:
            raise serializers.ValidationError(
                "This book is currently borrowed by another user."
            )

        return value

    def validate(self, attrs):
        """Validate user can borrow books."""
        user = self.context["request"].user

        # check if user can borrow more books
        if not user.can_borrow_books():
            raise serializers.ValidationError(
                "You have reached your maximum book borrowing limit."
            )

        # check if user already borrowed this book and hasn't returned it
        book_id = attrs["book_id"]
        existing_loan = Loan.objects.filter(
            user=user, book_id=book_id, returned_at__isnull=True
        ).first()

        if existing_loan:
            raise serializers.ValidationError("You have already borrowed this book.")

        return attrs

    def create(self, validated_data):
        """Create a new loan record."""
        user = self.context["request"].user
        book = Book.objects.get(id=validated_data["book_id"])

        loan = Loan.objects.create(user=user, book=book)
        return loan


class ReturnBookSerializer(serializers.Serializer):
    """
    Serializer for returning a book.
    """

    loan_id = serializers.IntegerField()

    def validate_loan_id(self, value):
        """Validate that loan exists and belongs to the user."""
        user = self.context["request"].user

        try:
            loan = Loan.objects.get(id=value)
        except Loan.DoesNotExist:
            raise serializers.ValidationError("Loan with this ID does not exist.")

        # check if loan belongs to the current user (unless user is staff)
        if not user.is_staff and loan.user != user:
            raise serializers.ValidationError(
                "You can only return your own borrowed books."
            )

        # check if book is already returned
        if loan.is_returned():
            raise serializers.ValidationError("This book has already been returned.")

        return value

    def save(self):
        """Mark the loan as returned."""
        loan = Loan.objects.get(id=self.validated_data["loan_id"])
        loan.returned_at = timezone.now().date()
        loan.save()
        return loan
