import pytest
from decimal import Decimal
from io import BytesIO
from datetime import timedelta

from django.utils import timezone
from django.core.files.uploadedfile import SimpleUploadedFile
from djmoney.money import Money
from rest_framework.test import APIClient

from apps.listings.models import Listing, Photo
from apps.users.models import BookingUser
from apps.bookings.models import Booking
from core.models import BookingStatus


@pytest.fixture
def user(db):
    """
    Create and return a test user.
    """
    return BookingUser.objects.create_user(
        email="tenant@example.com",
        password="TestPassword1!",
        first_name="Test",
        last_name="Tenant",
        phone="+491234567890",
    )


@pytest.fixture
def owner(user):
    """
    Return a test user who acts as a listing owner.
    """
    return user


@pytest.fixture
def listing(owner):
    """
    Create and return a test listing.
    """
    return Listing.objects.create(
        owner=owner,
        title="Nice apartment in Berlin",
        description="Comfortable apartment in the city center.",
        country="DE",
        city="Berlin",
        district="Mitte",
        street="Example Street",
        house_number="10",
        apartment_number="5",
        price_per_night=Money(100, "EUR"),
        rooms="2",
        is_active=True,
    )


@pytest.fixture
def photo(listing):
    """
    Create and return a test photo for the listing.
    """
    image = SimpleUploadedFile(
        name="test.jpg",
        content=(
            b"\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01"
            b"\x00\x00\x01\x00\x01\x00\x00\xff\xd9"
        ),
        content_type="image/jpeg",
    )

    return Photo.objects.create(
        listing=listing,
        image=image,
        position=1,
    )


@pytest.fixture
def api_client():
    """
    Create and return an API client for testing HTTP requests.
    """
    return APIClient()


@pytest.fixture
def booking_owner(db):
    """
    Create a separate user who acts as a listing owner for booking tests.
    """
    return BookingUser.objects.create_user(
        email="bookingowner@example.com",
        password="TestPassword1!",
        first_name="Booking",
        last_name="Owner",
        phone="+491234567890",
    )


@pytest.fixture
def booking_listing(booking_owner):
    """
    Create a listing owned by a separate booking owner.
    """
    return Listing.objects.create(
        owner=booking_owner,
        title="Booking apartment",
        description="Apartment for booking tests.",
        country="DE",
        city="Berlin",
        district="Mitte",
        street="Booking Street",
        house_number="20",
        apartment_number="10",
        price_per_night=Money(100, "EUR"),
        rooms="2",
        is_active=True,
    )


@pytest.fixture
def completed_booking(user, booking_listing):
    """
    Create a completed booking that can be reviewed by the tenant.
    """
    now = timezone.now()

    return Booking.objects.create(
        tenant=user,
        listing=booking_listing,
        date_start=now - timedelta(days=5),
        date_end=now - timedelta(days=2),

        snapshot_title=booking_listing.title,
        snapshot_country=booking_listing.country,
        snapshot_city=booking_listing.city,
        snapshot_district=booking_listing.district,
        snapshot_street=booking_listing.street,
        snapshot_house_number=booking_listing.house_number,
        snapshot_apartment_number=booking_listing.apartment_number,

        snapshot_first_name=user.first_name,
        snapshot_last_name=user.last_name,
        snapshot_email=user.email,
        snapshot_price_per_night=booking_listing.price_per_night,

        status=BookingStatus.COMPLETED,
    )