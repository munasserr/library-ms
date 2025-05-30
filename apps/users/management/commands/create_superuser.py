from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.db import transaction

User = get_user_model()


class Command(BaseCommand):
    """
    Management command to create a superuser for development.

    This command creates a superuser with predefined credentials
    for easy development setup.
    """

    help = "Create a superuser for development"

    def add_arguments(self, parser):
        parser.add_argument(
            "--email",
            type=str,
            default="admin@library.com",
            help="Email for the superuser (default: admin@library.com)",
        )
        parser.add_argument(
            "--username",
            type=str,
            default="admin",
            help="Username for the superuser (default: admin)",
        )
        parser.add_argument(
            "--password",
            type=str,
            default="admin123",
            help="Password for the superuser (default: admin123)",
        )
        parser.add_argument(
            "--force", action="store_true", help="Force creation even if user exists"
        )

    def handle(self, *args, **options):
        email = options["email"]
        username = options["username"]
        password = options["password"]
        force = options["force"]

        try:
            with transaction.atomic():
                # see if user already exists
                if User.objects.filter(email=email).exists():
                    if force:
                        User.objects.filter(email=email).delete()
                        self.stdout.write(
                            self.style.WARNING(
                                f"Deleted existing user with email: {email}"
                            )
                        )
                    else:
                        self.stdout.write(
                            self.style.ERROR(
                                f"User with email {email} already exists. Use --force to override."
                            )
                        )
                        return

                # create superuser
                user = User.objects.create_superuser(
                    email=email,
                    username=username,
                    password=password,
                    first_name="Library",
                    last_name="Admin",
                )

                self.stdout.write(
                    self.style.SUCCESS(
                        f"Successfully created superuser:\n"
                        f"  Email: {user.email}\n"
                        f"  Username: {user.username}\n"
                        f"  Library Card: {user.library_card_number}"
                    )
                )

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error creating superuser: {str(e)}"))
