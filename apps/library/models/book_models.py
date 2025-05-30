from model_utils.models import TimeStampedModel
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError
from django.db import models
from datetime import date


class Author(TimeStampedModel):
    name = models.CharField(max_length=200)
    nationality = models.CharField(max_length=200)
    date_of_birth = models.DateField(null=True, blank=True)
    date_of_death = models.DateField(null=True, blank=True)

    @property
    def age(self):
        from apps.library.services.author_services import calculate_age

        return calculate_age(self.date_of_birth, self.date_of_death)

    def clean(self):
        if self.date_of_birth and self.date_of_birth > date.today():
            raise ValidationError("Date of birth cannot be in the future.")
        if self.date_of_death and self.date_of_death > date.today():
            raise ValidationError("Date of death cannot be in the future.")
        if self.date_of_birth and self.date_of_death:
            if self.date_of_death <= self.date_of_birth:
                raise ValidationError(
                    "Date of death cannot be before or equal date of birth."
                )

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Book(TimeStampedModel):
    LANGUAGE_CHOICES = [
        ("EN", "English"),
        ("FR", "French"),
        ("AR", "Arabic"),
        ("ES", "Spanish"),
        ("CZ", "Czech"),
        ("NL", "Dutch"),
    ]

    title = models.CharField(max_length=200)
    author = models.ForeignKey(
        Author, on_delete=models.SET_NULL, null=True, blank=True, related_name="books"
    )
    description = models.TextField()
    isbn = models.CharField(
        max_length=13,
        validators=[
            RegexValidator(
                regex=r"^\d{10}(\d{3})?$", message="ISBN must be 10 or 13 digits"
            )
        ],
    )
    publish_date = models.DateField()
    page_count = models.IntegerField()
    language = models.CharField(max_length=2, choices=LANGUAGE_CHOICES)
    is_available = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Book"
        verbose_name_plural = "Books"
        indexes = [
            models.Index(fields=["title"]),
            models.Index(fields=["author"]),
        ]
        unique_together = ["title", "author", "publish_date"]
        ordering = ["-publish_date"]

    def clean(self):
        if self.publish_date > date.today():
            raise ValidationError("Publish date cannot be in the future.")
        if self.page_count <= 0:
            raise ValidationError("Page count must be greater than 0.")

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.title} - {self.author.name if self.author else 'Unknown'}"
