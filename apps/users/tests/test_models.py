import pytest
from django.db import IntegrityError

from apps.users.models import BookingUser


def test_user_creation(user):
    """
    Check that a test user is created correctly.
    """
    assert user.email == "tenant@example.com"
    assert user.first_name == "Test"
    assert user.last_name == "Tenant"
    assert user.phone == "+491234567890"
    assert user.is_active is True


def test_user_has_uuid_and_timestamps(user):
    """
    Check that a user has UUID and timestamp fields.
    """
    assert user.id is not None
    assert user.created_at is not None
    assert user.updated_at is not None


def test_user_password_is_hashed(user):
    """
    Check that the user's password is stored as a hash.
    """
    assert user.password != "TestPassword1!"
    assert user.check_password("TestPassword1!") is True


def test_user_uses_email_as_username_field():
    """
    Check that email is used as the username field.
    """
    assert BookingUser.USERNAME_FIELD == "email"


def test_user_str(user):
    """
    Check the string representation of a user.
    """
    assert str(user) == user.email


def test_user_email_is_unique(user):
    """
    Check that duplicate email cannot be used for another user.
    """
    with pytest.raises(IntegrityError):
        BookingUser.objects.create_user(
            email=user.email,
            password="AnotherPassword1!",
            first_name="Another",
            last_name="User",
            phone="+491234567891",
        )


def test_create_superuser(db):
    """
    Check that a superuser is created with the required flags.
    """
    user = BookingUser.objects.create_superuser(
        email="admin@example.com",
        password="AdminPassword1!",
    )

    assert user.email == "admin@example.com"
    assert user.is_staff is True
    assert user.is_superuser is True
    assert user.is_active is True
    assert user.check_password("AdminPassword1!") is True