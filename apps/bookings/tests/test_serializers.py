from datetime import timedelta

from django.utils import timezone
from djmoney.money import Money

from apps.bookings.models import Booking
from apps.bookings.serializers import BookingCreateSerializer, BookingSerializer
from core.models import BookingStatus


def test_booking_create_serializer_returns_valid_data(listing):
    """
    Check that valid booking creation data passes serializer validation.
    """
    now = timezone.now()

    data = {
        "listing": str(listing.id),
        "date_start": (
            now + timedelta(days=10)
        ).replace(hour=14, minute=0, second=0, microsecond=0),
        "date_end": (
            now + timedelta(days=12)
        ).replace(hour=11, minute=0, second=0, microsecond=0),
    }

    serializer = BookingCreateSerializer(data=data)

    assert serializer.is_valid() is True


def test_booking_create_serializer_requires_listing():
    """
    Check that listing is required.
    """
    now = timezone.now()

    data = {
        "date_start": (
            now + timedelta(days=10)
        ).replace(hour=14, minute=0, second=0, microsecond=0),
        "date_end": (
            now + timedelta(days=12)
        ).replace(hour=11, minute=0, second=0, microsecond=0),
    }

    serializer = BookingCreateSerializer(data=data)

    assert serializer.is_valid() is True
    assert serializer.validated_data.get("listing") is None


def test_booking_create_serializer_rejects_invalid_date_order(listing):
    """
    Check that check-out must be later than check-in.
    """
    now = timezone.now()

    data = {
        "listing": str(listing.id),
        "date_start": (
            now + timedelta(days=12)
        ).replace(hour=14, minute=0, second=0, microsecond=0),
        "date_end": (
            now + timedelta(days=10)
        ).replace(hour=11, minute=0, second=0, microsecond=0),
    }

    serializer = BookingCreateSerializer(data=data)

    assert serializer.is_valid() is False
    assert "date_end" in serializer.errors


def test_booking_create_serializer_rejects_past_date(listing):
    """
    Check that booking cannot start in the past.
    """
    now = timezone.now()

    data = {
        "listing": str(listing.id),
        "date_start": (
            now - timedelta(days=1)
        ).replace(hour=14, minute=0, second=0, microsecond=0),
        "date_end": (
            now + timedelta(days=2)
        ).replace(hour=11, minute=0, second=0, microsecond=0),
    }

    serializer = BookingCreateSerializer(data=data)

    assert serializer.is_valid() is False
    assert "date_start" in serializer.errors


def test_booking_create_serializer_rejects_invalid_check_in_time(listing):
    """
    Check that check-in time must be within the allowed period.
    """
    now = timezone.now()

    data = {
        "listing": str(listing.id),
        "date_start": (
            now + timedelta(days=10)
        ).replace(hour=13, minute=0, second=0, microsecond=0),
        "date_end": (
            now + timedelta(days=12)
        ).replace(hour=11, minute=0, second=0, microsecond=0),
    }

    serializer = BookingCreateSerializer(data=data)

    assert serializer.is_valid() is False
    assert "date_start" in serializer.errors


def test_booking_create_serializer_rejects_invalid_check_out_time(listing):
    """
    Check that check-out time must be within the allowed period.
    """
    now = timezone.now()

    data = {
        "listing": str(listing.id),
        "date_start": (
            now + timedelta(days=10)
        ).replace(hour=14, minute=0, second=0, microsecond=0),
        "date_end": (
            now + timedelta(days=12)
        ).replace(hour=12, minute=0, second=0, microsecond=0),
    }

    serializer = BookingCreateSerializer(data=data)

    assert serializer.is_valid() is False
    assert "date_end" in serializer.errors


def test_booking_serializer_returns_booking_data(listing, user):
    """
    Check that BookingSerializer returns booking information.
    """
    booking = Booking.objects.create(
        tenant=user,
        listing=listing,
        date_start="2026-10-01T14:00:00Z",
        date_end="2026-10-05T11:00:00Z",
        snapshot_title=listing.title,
        snapshot_country=listing.country,
        snapshot_city=listing.city,
        snapshot_district=listing.district,
        snapshot_street=listing.street,
        snapshot_house_number=listing.house_number,
        snapshot_apartment_number=listing.apartment_number,
        snapshot_first_name=user.first_name,
        snapshot_last_name=user.last_name,
        snapshot_email=user.email,
        snapshot_price_per_night=Money(100, "EUR"),
        status=BookingStatus.PENDING,
    )

    serializer = BookingSerializer(booking)

    assert serializer.data["id"] == str(booking.id)
    assert serializer.data["listing"] == listing.id
    assert serializer.data["status"] == BookingStatus.PENDING
    assert serializer.data["snapshot_title"] == listing.title
    assert serializer.data["snapshot_city"] == listing.city
    assert serializer.data["snapshot_first_name"] == user.first_name
    assert serializer.data["snapshot_email"] == user.email


def test_booking_serializer_snapshot_fields_are_read_only(listing, user):
    """
    Check that snapshot fields and status cannot be changed through serializer.
    """
    booking = Booking.objects.create(
        tenant=user,
        listing=listing,
        date_start="2026-10-01T14:00:00Z",
        date_end="2026-10-05T11:00:00Z",
        snapshot_title=listing.title,
        snapshot_country=listing.country,
        snapshot_city=listing.city,
        snapshot_district=listing.district,
        snapshot_street=listing.street,
        snapshot_house_number=listing.house_number,
        snapshot_apartment_number=listing.apartment_number,
        snapshot_first_name=user.first_name,
        snapshot_last_name=user.last_name,
        snapshot_email=user.email,
        snapshot_price_per_night=Money(100, "EUR"),
    )

    serializer = BookingSerializer(booking)

    assert serializer.fields["snapshot_title"].read_only is True
    assert serializer.fields["snapshot_country"].read_only is True
    assert serializer.fields["snapshot_city"].read_only is True
    assert serializer.fields["snapshot_first_name"].read_only is True
    assert serializer.fields["snapshot_email"].read_only is True
    assert serializer.fields["snapshot_price_per_night"].read_only is True
    assert serializer.fields["status"].read_only is True
    assert serializer.fields["created_at"].read_only is True
    assert serializer.fields["updated_at"].read_only is True