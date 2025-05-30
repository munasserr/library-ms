from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.db import models
from model_utils.models import TimeStampedModel


class CustomUser(AbstractUser, TimeStampedModel):
    """
    This model adds additional fields specific to the library management system
    while maintaining all the default Django user functionality.
    """

    email = models.EmailField(
        unique=True, help_text="Email address of the user. Must be unique."
    )

    phone_number = models.CharField(
        max_length=15,
        blank=True,
        null=True,
        validators=[
            RegexValidator(
                regex=r"^\+?1?\d{9,15}$",
                message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed.",
            )
        ],
        help_text="Contact phone number",
    )

    date_of_birth = models.DateField(
        blank=True, null=True, help_text="User's date of birth"
    )

    is_verified = models.BooleanField(
        default=False,
        help_text="Designates whether this user's email has been verified.",
    )

    library_card_number = models.CharField(
        max_length=20,
        unique=True,
        blank=True,
        null=True,
        help_text="Unique library card number",
    )

    max_books_allowed = models.PositiveIntegerField(
        default=5,
        help_text="Maximum number of books the user can borrow simultaneously",
    )

    # Override USERNAME_FIELD to use email instead of username
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username", "first_name", "last_name"]

    class Meta:
        verbose_name = "User"
        verbose_name_plural = "Users"
        indexes = [
            models.Index(fields=["email"]),
            models.Index(fields=["library_card_number"]),
            models.Index(fields=["is_active", "is_verified"]),
        ]

    def __str__(self):
        return f"{self.get_full_name()} ({self.email})"

    def get_full_name(self):
        """Return the full name of the user."""
        return f"{self.first_name} {self.last_name}".strip() or self.username

    def get_short_name(self):
        """Return the short name for the user."""
        return self.first_name or self.username

    @property
    def current_loans_count(self):
        """Return the number of currently active loans for this user."""
        return self.loans.filter(returned_at__isnull=True).count()

    def can_borrow_books(self):
        """Check if the user can borrow more books."""
        return self.current_loans_count < self.max_books_allowed

    def save(self, *args, **kwargs):
        """Override save to generate library card number if not provided."""
        if not self.library_card_number and self.pk:
            # generate library card number after the user is saved
            self.library_card_number = f"LIB{self.pk:06d}"
        super().save(*args, **kwargs)

        # save again if the library card number is not provided
        if not self.library_card_number:
            self.library_card_number = f"LIB{self.pk:06d}"
            super().save(update_fields=["library_card_number"])
