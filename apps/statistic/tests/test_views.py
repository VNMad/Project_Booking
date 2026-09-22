import pytest
from datetime import timedelta

from django.core.cache import cache
from django.urls import reverse
from django.utils import timezone

from apps.bookings.models import Booking
from apps.reviews.models import Review
from core.models import BookingStatus


@pytest.fixture(autouse=True)
def clear_throttle_cache():
    """
    Clear the cache before and after each test
    so throttle counters do not leak between tests.
    """
    cache.clear()

    yield

    cache.clear()


def create_booking(
    *,
    tenant,
    listing,
    status,
    days_start=10,
    days_end=12,
):
    """
    Create a booking for statistics tests.

    The booking contains all required snapshot fields.
    """
    now = timezone.now()

    return Booking.objects.create(
        tenant=tenant,
        listing=listing,
        date_start=now + timedelta(days=days_start),
        date_end=now + timedelta(days=days_end),

        snapshot_title=listing.title,
        snapshot_country=listing.country,
        snapshot_city=listing.city,
        snapshot_district=listing.district,
        snapshot_street=listing.street,
        snapshot_house_number=listing.house_number,
        snapshot_apartment_number=listing.apartment_number,

        snapshot_first_name=tenant.first_name,
        snapshot_last_name=tenant.last_name,
        snapshot_email=tenant.email,
        snapshot_price_per_night=listing.price_per_night,

        status=status,
    )


def test_public_listing_statistics_available_for_anonymous_user(
    api_client,
    booking_listing,
):
    """
    Check that public listing statistics are available
    without authentication.
    """
    url = reverse(
        "listing-statistics-detail",
        kwargs={"pk": booking_listing.id},
    )

    response = api_client.get(url)

    assert response.status_code == 200
    assert response.data["listing_id"] == str(booking_listing.id)


def test_public_listing_statistics_without_reviews(
    api_client,
    booking_listing,
):
    """
    Check public statistics when the listing has no reviews.
    """
    url = reverse(
        "listing-statistics-detail",
        kwargs={"pk": booking_listing.id},
    )

    response = api_client.get(url)

    assert response.status_code == 200
    assert response.data["reviews_count"] == 0
    assert response.data["average_cleanliness"] is None
    assert response.data["average_location"] is None


def test_public_listing_statistics_returns_review_averages(
    api_client,
    user,
    booking_listing,
):
    """
    Check that public statistics calculate review averages correctly.
    """
    first_booking = create_booking(
        tenant=user,
        listing=booking_listing,
        status=BookingStatus.COMPLETED,
        days_start=-10,
        days_end=-8,
    )

    second_booking = create_booking(
        tenant=user,
        listing=booking_listing,
        status=BookingStatus.COMPLETED,
        days_start=-6,
        days_end=-4,
    )

    Review.objects.create(
        booking=first_booking,
        cleanliness_rating=5,
        location_rating=4,
        comment="First review.",
    )

    Review.objects.create(
        booking=second_booking,
        cleanliness_rating=3,
        location_rating=5,
        comment="Second review.",
    )

    url = reverse(
        "listing-statistics-detail",
        kwargs={"pk": booking_listing.id},
    )

    response = api_client.get(url)

    assert response.status_code == 200
    assert response.data["reviews_count"] == 2
    assert response.data["average_cleanliness"] == 4.0
    assert response.data["average_location"] == 4.5


def test_public_statistics_rejects_inactive_listing(
    api_client,
    booking_listing,
):
    """
    Check that public statistics are unavailable
    for an inactive listing.
    """
    booking_listing.is_active = False
    booking_listing.save(update_fields=["is_active"])

    url = reverse(
        "listing-statistics-detail",
        kwargs={"pk": booking_listing.id},
    )

    response = api_client.get(url)

    assert response.status_code == 404


def test_public_statistics_rejects_deleted_listing(
    api_client,
    booking_listing,
):
    """
    Check that public statistics are unavailable
    for a soft-deleted listing.
    """
    booking_listing.deleted_at = timezone.now()
    booking_listing.save(update_fields=["deleted_at"])

    url = reverse(
        "listing-statistics-detail",
        kwargs={"pk": booking_listing.id},
    )

    response = api_client.get(url)

    assert response.status_code == 404


def test_public_statistics_returns_404_for_missing_listing(api_client, db):
    """
    Check that a nonexistent listing returns 404.
    """
    listing_id = "00000000-0000-0000-0000-000000000000"

    url = reverse(
        "listing-statistics-detail",
        kwargs={"pk": listing_id},
    )

    response = api_client.get(url)

    assert response.status_code == 404


def test_owner_statistics_requires_authentication(
    api_client,
    booking_listing,
):
    """
    Check that private owner statistics require authentication.
    """
    url = reverse(
        "listing-statistics-owner-statistics",
        kwargs={"pk": booking_listing.id},
    )

    response = api_client.get(url)

    assert response.status_code == 401


def test_non_owner_cannot_view_owner_statistics(
    api_client,
    user,
    booking_listing,
):
    """
    Check that an authenticated non-owner cannot view
    private listing statistics.
    """
    api_client.force_authenticate(user=user)

    url = reverse(
        "listing-statistics-owner-statistics",
        kwargs={"pk": booking_listing.id},
    )

    response = api_client.get(url)

    assert response.status_code == 403


def test_owner_can_view_listing_statistics(
    api_client,
    booking_owner,
    booking_listing,
):
    """
    Check that the listing owner can view private statistics.
    """
    api_client.force_authenticate(user=booking_owner)

    url = reverse(
        "listing-statistics-owner-statistics",
        kwargs={"pk": booking_listing.id},
    )

    response = api_client.get(url)

    assert response.status_code == 200
    assert response.data["listing_id"] == str(booking_listing.id)


def test_owner_statistics_returns_booking_counts(
    api_client,
    user,
    booking_owner,
    booking_listing,
):
    """
    Check that private statistics calculate booking counts
    by status correctly.
    """
    create_booking(
        tenant=user,
        listing=booking_listing,
        status=BookingStatus.CONFIRMED,
        days_start=10,
        days_end=12,
    )

    create_booking(
        tenant=user,
        listing=booking_listing,
        status=BookingStatus.COMPLETED,
        days_start=-10,
        days_end=-8,
    )

    create_booking(
        tenant=user,
        listing=booking_listing,
        status=BookingStatus.CANCELLED,
        days_start=20,
        days_end=22,
    )

    api_client.force_authenticate(user=booking_owner)

    url = reverse(
        "listing-statistics-owner-statistics",
        kwargs={"pk": booking_listing.id},
    )

    response = api_client.get(url)

    assert response.status_code == 200

    assert response.data["bookings_count"] == 3
    assert response.data["confirmed_bookings"] == 1
    assert response.data["completed_bookings"] == 1


def test_owner_statistics_returns_review_statistics(
    api_client,
    user,
    booking_owner,
    booking_listing,
):
    """
    Check that private owner statistics include review statistics.
    """
    first_booking = create_booking(
        tenant=user,
        listing=booking_listing,
        status=BookingStatus.COMPLETED,
        days_start=-10,
        days_end=-8,
    )

    second_booking = create_booking(
        tenant=user,
        listing=booking_listing,
        status=BookingStatus.COMPLETED,
        days_start=-6,
        days_end=-4,
    )

    Review.objects.create(
        booking=first_booking,
        cleanliness_rating=5,
        location_rating=3,
    )

    Review.objects.create(
        booking=second_booking,
        cleanliness_rating=4,
        location_rating=5,
    )

    api_client.force_authenticate(user=booking_owner)

    url = reverse(
        "listing-statistics-owner-statistics",
        kwargs={"pk": booking_listing.id},
    )

    response = api_client.get(url)

    assert response.status_code == 200

    assert response.data["reviews_count"] == 2
    assert response.data["average_cleanliness"] == 4.5
    assert response.data["average_location"] == 4.0

    assert response.data["bookings_count"] == 2
    assert response.data["completed_bookings"] == 2
    assert response.data["confirmed_bookings"] == 0


def test_owner_statistics_returns_404_for_missing_listing(api_client, booking_owner):
    """
    Check that private statistics return 404
    for a nonexistent listing.
    """
    api_client.force_authenticate(user=booking_owner)

    listing_id = "00000000-0000-0000-0000-000000000000"

    url = reverse("listing-statistics-owner-statistics", kwargs={"pk": listing_id})

    response = api_client.get(url)

    assert response.status_code == 404