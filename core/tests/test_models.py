import pytest
from django.db import models
from django.core.exceptions import ValidationError
from apps.users.models import BookingUser

from core.models import (
    BookingStatus,
    EuropeanCountry,
    RoomCount,
    TimeStampedModel,
    UniqueID,
)


def test_user_phone_validation(db):
    """
    Check that BookingUser validates the phone number.
    """
    user = BookingUser(
        email="phone-test@example.com",
        first_name="Phone",
        last_name="Test",
        phone="491234567890",
    )

    with pytest.raises(ValidationError):
        user.full_clean()


def test_unique_id_is_abstract():
    """
    Check that UniqueID is an abstract model.
    """
    assert UniqueID._meta.abstract is True


def test_unique_id_has_uuid_primary_key():
    """
    Check that UniqueID provides a UUID primary key.
    """
    field = UniqueID._meta.get_field("id")

    assert isinstance(field, models.UUIDField)
    assert field.primary_key is True
    assert field.editable is False


def test_timestamped_model_is_abstract():
    """
    Check that TimeStampedModel is an abstract model.
    """
    assert TimeStampedModel._meta.abstract is True


def test_timestamped_model_has_timestamps():
    """
    Check that TimeStampedModel provides created_at and updated_at fields.
    """
    created_at = TimeStampedModel._meta.get_field("created_at")
    updated_at = TimeStampedModel._meta.get_field("updated_at")

    assert isinstance(created_at, models.DateTimeField)
    assert isinstance(updated_at, models.DateTimeField)

    assert created_at.auto_now_add is True
    assert updated_at.auto_now is True


def test_room_count_choices():
    """
    Check the available room-count choices.
    """
    assert RoomCount.ONE == "1"
    assert RoomCount.TWO == "2"
    assert RoomCount.THREE == "3"
    assert RoomCount.FOUR == "4"
    assert RoomCount.FIVE == "5"
    assert RoomCount.FIVE_PLUS == "5+"


def test_booking_status_choices():
    """
    Check the available booking statuses.
    """
    assert BookingStatus.PENDING == "pending"
    assert BookingStatus.CONFIRMED == "confirmed"
    assert BookingStatus.REJECTED == "rejected"
    assert BookingStatus.CANCELLED == "cancelled"
    assert BookingStatus.COMPLETED == "completed"


def test_european_country_germany():
    """
    Check that Germany has the expected country code.
    """
    assert EuropeanCountry.GERMANY == "DE"


def test_european_country_ukraine():
    """
    Check that Ukraine has the expected country code.
    """
    assert EuropeanCountry.UKRAINE == "UA"


def test_european_country_united_kingdom():
    """
    Check that the United Kingdom has the expected country code.
    """
    assert EuropeanCountry.UNITED_KINGDOM == "GB"