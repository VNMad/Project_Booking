from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import (validate_password as django_validate_password)
from rest_framework import serializers

from core.validators import validate_password


User = get_user_model()


class RegisterSerializer(serializers.ModelSerializer):
    """
    Serializer for creating a new user account.
    The user registers with a first name, last name, email,
    phone number, and password.
    """
    password = serializers.CharField(write_only=True, min_length=8, help_text=(
            "User password"
            "It must contain at least 8 characters, one uppercase letter, one lowercase letter,"
            "one digit and one special character."))
    email = serializers.EmailField(help_text="User email address. Used as the login identifier.")

    class Meta:
        model = User
        fields = [
            "first_name",
            "last_name",
            "email",
            "phone",
            "password",
        ]
        extra_kwargs = {
            "first_name": {"help_text": "User's first name."},
            "last_name": {"help_text": "User's last name."},
            "phone": {"help_text": "User's phone number."},
        }

    def validate_email(self, value):
        value = value.strip().lower()

        if not value:
            raise serializers.ValidationError("Email is required.")

        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError("This email is already registered.")
        return value

    def validate_password(self, value):
        if not value:
            raise serializers.ValidationError("Password is required.")
        validate_password(value)
        django_validate_password(value)
        return value

    def create(self, validated_data):
        return User.objects.create_user(
            email=validated_data["email"],
            password=validated_data["password"],
            first_name=validated_data["first_name"],
            last_name=validated_data["last_name"],
            phone=validated_data["phone"],
        )


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for displaying and updating the authenticated user's profile.
    Email, account status, and timestamps are read-only.
    """

    class Meta:
        model = User
        fields = [
            "first_name",
            "last_name",
            "email",
            "phone",
            "is_active",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "email",
            "is_active",
            "created_at",
            "updated_at",
        ]
        extra_kwargs = {
            "first_name": {"help_text": "User's first name."},
            "last_name": {"help_text": "User's last name."},
            "email": {"help_text": "User email address. Used as the login identifier."},
            "phone": {"help_text": "User's phone number."},
            "is_active": {"help_text": "Indicates whether the user account is active."},
            "created_at": {"help_text": "Date and time when the user account was created."},
            "updated_at": {"help_text": "Date and time when the user account was last updated."},
        }