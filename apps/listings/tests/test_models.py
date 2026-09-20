from django.db import IntegrityError

import pytest
from apps.listings.models import Listing, Photo


def test_listing_creation(listing):
    """
    Check that a listing is created with the expected data.
    """
    assert listing.title == "Nice apartment in Berlin"
    assert listing.city == "Berlin"
    assert listing.country == "DE"
    assert listing.district == "Mitte"
    assert listing.house_number == "10"
    assert listing.apartment_number == "5"
    assert listing.rooms == "2"
    assert listing.price_per_night.amount == 100
    assert listing.price_per_night.currency.code == "EUR"
    assert listing.is_active is True
    assert listing.deleted_at is None


def test_listing_owner(listing, owner):
    """
    Check that the listing is connected to its owner.
    """
    assert listing.owner == owner
    assert listing.owner_id == owner.id


def test_listing_default_active_status(owner):
    """
    Check that a new listing is active by default.
    """

    listing = Listing.objects.create(
        owner=owner,
        title="Another apartment",
        description="Test description.",
        country="DE",
        city="Hamburg",
        district="Altona",
        street="Test Street",
        house_number="20",
        apartment_number="3",
        price_per_night=100,
        rooms="1",
    )

    assert listing.is_active is True
    assert listing.deleted_at is None


def test_listing_unique_address(listing, owner):
    """
    Check that two listings cannot have the same address.
    """

    with pytest.raises(IntegrityError):
        Listing.objects.create(
            owner=owner,
            title="Duplicate apartment",
            description="Another description.",
            country=listing.country,
            city=listing.city,
            district=listing.district,
            street=listing.street,
            house_number=listing.house_number,
            apartment_number=listing.apartment_number,
            price_per_night=100,
            rooms="2",
        )


def test_photo_creation(photo, listing):
    """
    Check that a photo is connected to the listing.
    """
    assert photo.listing == listing
    assert photo.listing_id == listing.id
    assert photo.position == 1


def test_photo_positions_are_unique(listing, photo):
    """
    Check that two photos of the same listing cannot have the same position.
    """

    image = photo.image

    with pytest.raises(IntegrityError):
        Photo.objects.create(
            listing=listing,
            image=image,
            position=1,
        )