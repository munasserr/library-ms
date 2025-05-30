from rest_framework import serializers
from django.contrib.auth import authenticate
from apps.users.models import CustomUser


class UserLoginSerializer(serializers.Serializer):
    """
    Serializer for user authentication.

    Handles login using email and password with comprehensive validation.
    """

    email = serializers.EmailField(required=True)
    password = serializers.CharField(required=True, style={"input_type": "password"})

    def validate(self, attrs):
        """Validate user credentials."""
        email = attrs.get("email")
        password = attrs.get("password")

        if email and password:
            # authenticate the user
            user = authenticate(username=email, password=password)

            if not user:
                # check if user exists, but credentials are wrong
                if CustomUser.objects.filter(email=email).exists():
                    raise serializers.ValidationError({"detail": ["Invalid password."]})
                else:
                    raise serializers.ValidationError(
                        {"detail": ["No account found with this email address."]}
                    )

            if not user.is_active:
                raise serializers.ValidationError(
                    {"detail": ["User account is disabled."]}
                )

            attrs["user"] = user
            return attrs
        else:
            raise serializers.ValidationError(
                {"detail": ["Must include email and password."]}
            )
