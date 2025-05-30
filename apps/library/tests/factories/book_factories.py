import factory
from factory.django import DjangoModelFactory
from factory import fuzzy
from datetime import date, timedelta
from apps.library.models.book_models import Author, Book


class AuthorFactory(DjangoModelFactory):
    class Meta:
        model = Author

    name = factory.Faker("name")
    nationality = factory.Faker("country")
    date_of_birth = factory.Faker("date_of_birth", minimum_age=20, maximum_age=100)
    date_of_death = None


class BookFactory(DjangoModelFactory):
    class Meta:
        model = Book

    title = factory.Faker("catch_phrase")
    author = factory.SubFactory(AuthorFactory)
    description = factory.Faker("text", max_nb_chars=500)
    isbn = factory.Faker(
        "isbn13", separator=""
    )  # This will generate valid 13-digit ISBNs
    publish_date = factory.LazyFunction(
        lambda: date.today() - timedelta(days=fuzzy.FuzzyInteger(0, 3650).fuzz())
    )
    page_count = fuzzy.FuzzyInteger(50, 1000)
    language = factory.fuzzy.FuzzyChoice([x[0] for x in Book.LANGUAGE_CHOICES])
    is_available = True
