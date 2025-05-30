from .book_serializers import (
    AuthorSerializer,
    AuthorCreateUpdateSerializer,
    BookSerializer,
    BookDetailSerializer,
    BookCreateSerializer,
    BookUpdateSerializer,
    BookCreateUpdateSerializer,  # Deprecated - for backward compatibility
)
from .loan_serializers import LoanSerializer, BorrowBookSerializer, ReturnBookSerializer

__all__ = [
    "AuthorSerializer",
    "AuthorCreateUpdateSerializer",
    "BookSerializer",
    "BookDetailSerializer",
    "BookCreateSerializer",
    "BookUpdateSerializer",
    "BookCreateUpdateSerializer",  # Deprecated
    "LoanSerializer",
    "BorrowBookSerializer",
    "ReturnBookSerializer",
]
