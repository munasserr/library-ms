from rest_framework import serializers
from apps.library.models import Book, Author
from datetime import date


class AuthorSerializer(serializers.ModelSerializer):
    """Serializer for Author model - read operations."""

    age = serializers.ReadOnlyField()

    class Meta:
        model = Author
        fields = ["id", "name", "nationality", "date_of_birth", "date_of_death", "age"]


class AuthorCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer for creating and updating authors - admin only."""

    class Meta:
        model = Author
        fields = ["id", "name", "nationality", "date_of_birth", "date_of_death"]

    def validate(self, attrs):
        """Validate author data."""
        date_of_birth = attrs.get("date_of_birth")
        date_of_death = attrs.get("date_of_death")

        if date_of_birth and date_of_birth > date.today():
            raise serializers.ValidationError(
                {"date_of_birth": "Date of birth cannot be in the future."}
            )

        if date_of_death and date_of_death > date.today():
            raise serializers.ValidationError(
                {"date_of_death": "Date of death cannot be in the future."}
            )

        if date_of_birth and date_of_death and date_of_death <= date_of_birth:
            raise serializers.ValidationError(
                {"date_of_death": "Date of death must be after date of birth."}
            )

        return super().validate(attrs)


class BookSerializer(serializers.ModelSerializer):
    """
    Serializer for Book model - used for listing books.
    """

    author_name = serializers.CharField(source="author.name", read_only=True)

    class Meta:
        model = Book
        fields = [
            "id",
            "title",
            "author_name",
            "isbn",
            "publish_date",
            "language",
        ]


class BookDetailSerializer(serializers.ModelSerializer):
    """
    Detailed serializer for Book model - used for single book view.
    """

    author = AuthorSerializer(read_only=True)
    current_borrower = serializers.SerializerMethodField()

    class Meta:
        model = Book
        fields = [
            "id",
            "title",
            "author",
            "description",
            "isbn",
            "publish_date",
            "page_count",
            "language",
            "current_borrower",
            "created",
            "modified",
        ]

    def get_current_borrower(self, obj):
        """Get current borrower if book is borrowed."""
        active_loan = obj.loans.filter(returned_at__isnull=True).first()
        if active_loan:
            return {
                "user_id": active_loan.user.id,
                "username": active_loan.user.username,
                "borrowed_date": active_loan.created,
            }
        return None


class BookCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating books - admin only.
    Requires all fields including author_id.
    """

    author_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = Book
        fields = [
            "title",
            "author_id",
            "description",
            "isbn",
            "publish_date",
            "page_count",
            "language",
        ]

    def validate(self, attrs):
        """Validate book data."""
        if attrs.get("publish_date") and attrs["publish_date"] > date.today():
            raise serializers.ValidationError(
                {"publish_date": "Cannot be in the future."}
            )

        if attrs.get("page_count") is not None and attrs["page_count"] <= 0:
            raise serializers.ValidationError({"page_count": "Must be greater than 0."})

        return super().validate(attrs)

    def validate_author_id(self, value):
        """Validate that author exists."""
        try:
            Author.objects.get(id=value)
        except Author.DoesNotExist:
            raise serializers.ValidationError("Author with this ID does not exist.")
        return value

    def create(self, validated_data):
        """Create a new book."""
        author_id = validated_data.pop("author_id")
        validated_data["author"] = Author.objects.get(id=author_id)
        return Book.objects.create(**validated_data)


class BookUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for updating books - admin only.
    All fields are optional for partial updates.
    """

    author_id = serializers.IntegerField(write_only=True, required=False)

    class Meta:
        model = Book
        fields = [
            "title",
            "author_id",
            "description",
            "isbn",
            "publish_date",
            "page_count",
            "language",
        ]

    def validate(self, attrs):
        """Validate book data."""
        if attrs.get("publish_date") and attrs["publish_date"] > date.today():
            raise serializers.ValidationError(
                {"publish_date": "Cannot be in the future."}
            )

        if attrs.get("page_count") is not None and attrs["page_count"] <= 0:
            raise serializers.ValidationError({"page_count": "Must be greater than 0."})

        return super().validate(attrs)

    def validate_author_id(self, value):
        """Validate that author exists."""
        if value is not None:
            try:
                Author.objects.get(id=value)
            except Author.DoesNotExist:
                raise serializers.ValidationError("Author with this ID does not exist.")
        return value

    def update(self, instance, validated_data):
        """Update an existing book."""
        author_id = validated_data.pop("author_id", None)
        if author_id is not None:
            validated_data["author"] = Author.objects.get(id=author_id)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance


# (deprecated)
class BookCreateUpdateSerializer(BookCreateSerializer):
    """Deprecated: Use BookCreateSerializer or BookUpdateSerializer instead."""

    pass
