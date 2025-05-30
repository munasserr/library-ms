from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _
from .models import CustomUser


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    """
    Custom User Admin interface.

    Provides a comprehensive admin interface for managing users
    with all the custom fields included.
    """

    list_display = (
        "email",
        "username",
        "first_name",
        "last_name",
        "library_card_number",
        "is_verified",
        "is_active",
        "is_staff",
        "date_joined",
    )

    list_filter = (
        "is_active",
        "is_staff",
        "is_superuser",
        "is_verified",
        "date_joined",
        "last_login",
    )

    search_fields = (
        "email",
        "username",
        "first_name",
        "last_name",
        "library_card_number",
    )

    ordering = ("-date_joined",)

    readonly_fields = ("date_joined", "last_login", "current_loans_count")

    fieldsets = (
        (None, {"fields": ("email", "username", "password")}),
        (
            _("Personal info"),
            {"fields": ("first_name", "last_name", "phone_number", "date_of_birth")},
        ),
        (
            _("Library Information"),
            {
                "fields": (
                    "library_card_number",
                    "max_books_allowed",
                    "current_loans_count",
                )
            },
        ),
        (
            _("Permissions"),
            {
                "fields": (
                    "is_active",
                    "is_verified",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                ),
            },
        ),
        (_("Important dates"), {"fields": ("last_login", "date_joined")}),
    )

    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("email", "username", "password1", "password2"),
            },
        ),
        (
            _("Personal info"),
            {"fields": ("first_name", "last_name", "phone_number", "date_of_birth")},
        ),
        (_("Library Information"), {"fields": ("max_books_allowed",)}),
        (
            _("Permissions"),
            {
                "fields": ("is_active", "is_verified", "is_staff", "is_superuser"),
            },
        ),
    )

    def current_loans_count(self, obj):
        """Display current loans count in admin."""
        return obj.current_loans_count

    current_loans_count.short_description = "Active Loans"
