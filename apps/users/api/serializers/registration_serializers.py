from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from django.contrib.auth.password_validation import validate_password
from apps.users.models import CustomUser


class UserRegistrationSerializer(serializers.ModelSerializer):
    """
    Serializer for user registration.

    Handles user creation with comprehensive validation and secure password handling.
    """

    email = serializers.EmailField(
        required=True, validators=[UniqueValidator(queryset=CustomUser.objects.all())]
    )

    password = serializers.CharField(
        write_only=True,
        required=True,
        validators=[validate_password],
    )

    password_confirm = serializers.CharField(
        write_only=True,
        required=True,
    )

    first_name = serializers.CharField(required=True, max_length=150)
    last_name = serializers.CharField(required=True, max_length=150)

    class Meta:
        model = CustomUser
        fields = (
            "email",
            "username",
            "first_name",
            "last_name",
            "password",
            "password_confirm",
            "phone_number",
            "date_of_birth",
        )
        extra_kwargs = {
            "username": {"required": True},
            "phone_number": {"required": False},
            "date_of_birth": {"required": False},
        }

    def validate(self, attrs):
        """Validate that passwords match."""
        if attrs["password"] != attrs["password_confirm"]:
            raise serializers.ValidationError(
                {"password_confirm": "Password fields didn't match."}
            )
        return attrs

    def validate_username(self, value):
        """Validate username is unique and meets requirements."""
        if CustomUser.objects.filter(username=value).exists():
            raise serializers.ValidationError(
                "A user with this username already exists."
            )
        return value

    def create(self, validated_data):
        """Create a new user with encrypted password."""
        # remove password_confirm from validated_data
        validated_data.pop("password_confirm")

        # create user
        user = CustomUser.objects.create_user(
            email=validated_data["email"],
            username=validated_data["username"],
            first_name=validated_data["first_name"],
            last_name=validated_data["last_name"],
            phone_number=validated_data.get("phone_number"),
            date_of_birth=validated_data.get("date_of_birth"),
            password=validated_data["password"],
        )

        return user
