from django.db import models
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from model_utils.models import TimeStampedModel
from datetime import date

User = get_user_model()


class Loan(TimeStampedModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="loans")
    book = models.ForeignKey("Book", on_delete=models.CASCADE, related_name="loans")
    returned_at = models.DateField(null=True, blank=True)

    @property
    def borrowed_at(self):
        return self.created

    class Meta:
        unique_together = ("user", "book", "created")
        indexes = [
            models.Index(fields=["user"]),
            models.Index(fields=["book"]),
        ]
        ordering = ["-created"]

    def clean(self):
        if self.borrowed_at.date() > date.today():
            raise ValidationError("Borrow date cannot be in the future.")
        if self.returned_at and self.returned_at < self.borrowed_at.date():
            raise ValidationError("Return date cannot be before the borrow date.")

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def is_returned(self):
        return self.returned_at is not None

    def __str__(self):
        return f"{self.user} borrowed {self.book} on {self.borrowed_at}"
