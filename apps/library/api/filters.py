import django_filters
from django.db import models
from apps.library.models import Book, Loan


class BookFilter(django_filters.FilterSet):
    """
    Filter class for Book model with advanced filtering options.
    """

    title = django_filters.CharFilter(
        field_name="title",
        lookup_expr="icontains",
        help_text="Filter by book title (case-insensitive contains)",
    )

    isbn = django_filters.NumberFilter(
        field_name="isbn",
        lookup_expr="exact",
        help_text="Filter by book ISBN number",
    )

    author_name = django_filters.CharFilter(
        field_name="author__name",
        lookup_expr="icontains",
        help_text="Filter by author name (case-insensitive contains)",
    )

    language = django_filters.ChoiceFilter(
        choices=Book.LANGUAGE_CHOICES, help_text="Filter by book language"
    )

    publish_year = django_filters.NumberFilter(
        field_name="publish_date",
        lookup_expr="year",
        help_text="Filter by publication year",
    )

    publish_date_after = django_filters.DateFilter(
        field_name="publish_date",
        lookup_expr="gte",
        help_text="Filter books published after this date",
    )

    publish_date_before = django_filters.DateFilter(
        field_name="publish_date",
        lookup_expr="lte",
        help_text="Filter books published before this date",
    )

    page_count_min = django_filters.NumberFilter(
        field_name="page_count",
        lookup_expr="gte",
        help_text="Filter books with minimum page count",
    )

    page_count_max = django_filters.NumberFilter(
        field_name="page_count",
        lookup_expr="lte",
        help_text="Filter books with maximum page count",
    )

    is_available = django_filters.BooleanFilter(field_name="is_available")

    search = django_filters.CharFilter(
        method="filter_search",
        help_text="Search in title, author name, and description",
    )

    class Meta:
        model = Book
        fields = [
            "title",
            "author_name",
            "language",
            "publish_year",
            "publish_date_after",
            "publish_date_before",
            "page_count_min",
            "page_count_max",
            "is_available",
            "search",
        ]

    def filter_search(self, queryset, name, value):
        """Search across multiple fields."""
        if value:
            return queryset.filter(
                models.Q(title__icontains=value)
                | models.Q(author__name__icontains=value)
                | models.Q(description__icontains=value)
            ).distinct()
        return queryset


class LoanFilter(django_filters.FilterSet):
    """
    Filter class for Loan model with advanced filtering options.
    """

    user = django_filters.CharFilter(
        field_name="user__username",
        lookup_expr="icontains",
        help_text="Filter by username (case-insensitive contains)",
    )

    user_email = django_filters.CharFilter(
        field_name="user__email",
        lookup_expr="icontains",
        help_text="Filter by user email (case-insensitive contains)",
    )

    book_title = django_filters.CharFilter(
        field_name="book__title",
        lookup_expr="icontains",
        help_text="Filter by book title (case-insensitive contains)",
    )

    book_author = django_filters.CharFilter(
        field_name="book__author__name",
        lookup_expr="icontains",
        help_text="Filter by book author (case-insensitive contains)",
    )

    borrowed_after = django_filters.DateFilter(
        field_name="created",
        lookup_expr="date__gte",
        help_text="Filter loans borrowed after this date",
    )

    borrowed_before = django_filters.DateFilter(
        field_name="created",
        lookup_expr="date__lte",
        help_text="Filter loans borrowed before this date",
    )

    returned_after = django_filters.DateFilter(
        field_name="returned_at",
        lookup_expr="gte",
        help_text="Filter loans returned after this date",
    )

    returned_before = django_filters.DateFilter(
        field_name="returned_at",
        lookup_expr="lte",
        help_text="Filter loans returned before this date",
    )

    status = django_filters.ChoiceFilter(
        choices=[
            ("active", "Active (Not Returned)"),
            ("returned", "Returned"),
        ],
        method="filter_status",
        help_text="Filter by loan status",
    )

    class Meta:
        model = Loan
        fields = [
            "user",
            "user_email",
            "book_title",
            "book_author",
            "borrowed_after",
            "borrowed_before",
            "returned_after",
            "returned_before",
            "status",
        ]

    def filter_status(self, queryset, name, value):
        """Filter loans by status."""
        if value == "active":
            return queryset.filter(returned_at__isnull=True)
        elif value == "returned":
            return queryset.filter(returned_at__isnull=False)
        return queryset
