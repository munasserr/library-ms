from django.contrib import admin
from .models import Book, Author, Loan


class LoanInline(admin.TabularInline):
    model = Loan
    extra = 0
    fields = ("user", "returned_at")
    readonly_fields = ["user", "returned_at"]
    can_delete = False
    show_change_link = True


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "author",
        "language",
        "is_available",
        "publish_date",
        "page_count",
    )
    list_filter = ("language", "is_available", "author")
    search_fields = ("title", "author__name", "isbn")
    list_editable = ("is_available",)
    inlines = [LoanInline]
    fieldsets = (
        (None, {"fields": ("title", "author", "description")}),
        ("Publication", {"fields": ("isbn", "publish_date", "language", "page_count")}),
        ("Availability", {"fields": ("is_available",)}),
    )


@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    list_display = ("name", "nationality", "date_of_birth", "date_of_death")
    search_fields = ("name", "nationality")
    list_filter = ("nationality",)
    fieldsets = (
        (None, {"fields": ("name", "nationality")}),
        ("Life", {"fields": ("date_of_birth", "date_of_death")}),
    )


@admin.register(Loan)
class LoanAdmin(admin.ModelAdmin):
    list_display = ("book", "user", "returned_at")
    list_filter = ("returned_at", "book", "user")
    search_fields = ("book__title", "user__username")
    readonly_fields = ["returned_at"]
    actions = ["mark_as_returned"]

    def mark_as_returned(self, request, queryset):
        updated = 0
        for loan in queryset:
            if loan.returned_at is None:
                loan.returned_at = loan.modified = loan.modified.now()
                loan.book.is_available = True
                loan.book.save(update_fields=["is_available"])
                loan.save()
                updated += 1
        self.message_user(request, f"{updated} loans marked as returned.")

    mark_as_returned.short_description = "Mark selected loans as returned"
