import pytest
from decimal import Decimal
from io import BytesIO

from django.core.files.uploadedfile import SimpleUploadedFile
from djmoney.money import Money
from rest_framework.test import APIClient

from apps.listings.models import Listing, Photo
from apps.users.models import BookingUser


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