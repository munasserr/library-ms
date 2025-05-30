from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from apps.users.models import CustomUser


class UserProfileSerializer(serializers.ModelSerializer):
    """
    Serializer for user profile information.

    Used for retrieving and updating user profile data.
    """

    full_name = serializers.CharField(source="get_full_name", read_only=True)
    current_loans_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = CustomUser
        fields = (
            "id",
            "email",
            "username",
            "first_name",
            "last_name",
            "full_name",
            "phone_number",
            "date_of_birth",
            "library_card_number",
            "max_books_allowed",
            "current_loans_count",
            "is_verified",
            "date_joined",
            "last_login",
        )
        read_only_fields = (
            "id",
            "email",
            "username",
            "library_card_number",
            "max_books_allowed",
            "is_verified",
            "date_joined",
            "last_login",
        )


class ChangePasswordSerializer(serializers.Serializer):
    """
    Serializer for changing user password.

    Requires old password verification and validates new password.
    """

    old_password = serializers.CharField(
        required=True, style={"input_type": "password"}
    )
    new_password = serializers.CharField(
        required=True, validators=[validate_password], style={"input_type": "password"}
    )
    new_password_confirm = serializers.CharField(
        required=True, style={"input_type": "password"}
    )

    def validate_old_password(self, value):
        """Validate that the old password is correct."""
        user = self.context["request"].user
        if not user.check_password(value):
            raise serializers.ValidationError("Old password is incorrect.")
        return value

    def validate(self, attrs):
        """Validate that new passwords match."""
        if attrs["new_password"] != attrs["new_password_confirm"]:
            raise serializers.ValidationError(
                {"new_password_confirm": "New password fields didn't match."}
            )
        return attrs

    def save(self):
        """Save the new password."""
        user = self.context["request"].user
        user.set_password(self.validated_data["new_password"])
        user.save()
        return user
