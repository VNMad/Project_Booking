import pytest
from djmoney.money import Money
from datetime import datetime, timezone

from apps.bookings.models import Booking
from core.models import BookingStatus


def test_booking_creation(listing, user):
    """
    Check that a booking can be created with the required fields.
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

    assert booking.tenant == user
    assert booking.listing == listing
    assert booking.date_start is not None
    assert booking.date_end is not None
    assert booking.status == BookingStatus.PENDING


def test_booking_default_status(listing, user):
    """
    Check that a new booking has pending status by default.
    """
    booking = Booking.objects.create(
        tenant=user,
        listing=listing,
        date_start="2026-10-10T14:00:00Z",
        date_end="2026-10-12T11:00:00Z",
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

    assert booking.status == BookingStatus.PENDING


def test_booking_snapshots(listing, user):
    """
    Check that booking stores property and tenant snapshots.
    """
    booking = Booking.objects.create(
        tenant=user,
        listing=listing,
        date_start="2026-10-15T14:00:00Z",
        date_end="2026-10-18T11:00:00Z",
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

    assert booking.snapshot_title == listing.title
    assert booking.snapshot_country == listing.country
    assert booking.snapshot_city == listing.city
    assert booking.snapshot_district == listing.district
    assert booking.snapshot_street == listing.street
    assert booking.snapshot_house_number == listing.house_number
    assert booking.snapshot_apartment_number == listing.apartment_number

    assert booking.snapshot_first_name == user.first_name
    assert booking.snapshot_last_name == user.last_name
    assert booking.snapshot_email == user.email


def test_booking_price_snapshot(listing, user):
    """
    Check that booking stores the listing price snapshot.
    """
    booking = Booking.objects.create(
        tenant=user,
        listing=listing,
        date_start="2026-10-20T14:00:00Z",
        date_end="2026-10-22T11:00:00Z",
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

    assert booking.snapshot_price_per_night.amount == 100
    assert booking.snapshot_price_per_night.currency.code == "EUR"


def test_booking_string_representation(listing, user):
    """
    Check the string representation of a booking.
    """
    booking = Booking.objects.create(
        tenant=user,
        listing=listing,
        date_start=datetime(
            2026,
            10,
            25,
            14,
            0,
            tzinfo=timezone.utc,
        ),
        date_end=datetime(
            2026,
            10,
            28,
            11,
            0,
            tzinfo=timezone.utc,
        ),
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

    assert str(booking) == "Nice apartment in Berlin - 2026-10-25"