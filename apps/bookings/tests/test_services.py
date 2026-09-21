from datetime import timedelta

import pytest
from django.core.exceptions import ValidationError
from django.utils import timezone

from apps.bookings.models import Booking
from apps.bookings.services import (
    BookingNotFoundError,
    cancel_booking,
    complete_booking_if_finished,
    confirm_booking,
    create_booking,
    reject_booking,
)
from apps.users.models import BookingUser
from core.models import BookingStatus


def get_booking_dates():
    """
    Return valid dates for a booking service test.
    """
    now = timezone.now()

    date_start = (now + timedelta(days=10)).replace(
        hour=14,
        minute=0,
        second=0,
        microsecond=0,
    )
    date_end = (now + timedelta(days=12)).replace(
        hour=11,
        minute=0,
        second=0,
        microsecond=0,
    )

    return date_start, date_end


def test_create_booking_creates_pending_booking(user, booking_listing):
    date_start, date_end = get_booking_dates()

    booking = create_booking(
        tenant=user,
        listing_id=booking_listing.id,
        date_start=date_start,
        date_end=date_end,
    )

    assert booking.status == BookingStatus.PENDING
    assert booking.tenant == user
    assert booking.listing == booking_listing


def test_create_booking_creates_snapshots(user, booking_listing):
    date_start, date_end = get_booking_dates()

    booking = create_booking(
        tenant=user,
        listing_id=booking_listing.id,
        date_start=date_start,
        date_end=date_end,
    )

    assert booking.snapshot_title == booking_listing.title
    assert booking.snapshot_country == booking_listing.country
    assert booking.snapshot_city == booking_listing.city
    assert booking.snapshot_district == booking_listing.district
    assert booking.snapshot_street == booking_listing.street
    assert booking.snapshot_house_number == booking_listing.house_number
    assert booking.snapshot_apartment_number == booking_listing.apartment_number

    assert booking.snapshot_first_name == user.first_name
    assert booking.snapshot_last_name == user.last_name
    assert booking.snapshot_email == user.email

    assert booking.snapshot_price_per_night == booking_listing.price_per_night


def test_create_booking_rejects_inactive_listing(user, booking_listing):
    booking_listing.is_active = False
    booking_listing.save(update_fields=["is_active"])

    date_start, date_end = get_booking_dates()

    with pytest.raises(ValidationError):
        create_booking(
            tenant=user,
            listing_id=booking_listing.id,
            date_start=date_start,
            date_end=date_end,
        )


def test_create_booking_rejects_deleted_listing(user, booking_listing):
    booking_listing.deleted_at = timezone.now()
    booking_listing.save(update_fields=["deleted_at"])

    date_start, date_end = get_booking_dates()

    with pytest.raises(ValidationError):
        create_booking(
            tenant=user,
            listing_id=booking_listing.id,
            date_start=date_start,
            date_end=date_end,
        )


def test_create_booking_rejects_owner_booking_own_listing(
    booking_owner,
    booking_listing,
):
    date_start, date_end = get_booking_dates()

    with pytest.raises(ValidationError):
        create_booking(
            tenant=booking_owner,
            listing_id=booking_listing.id,
            date_start=date_start,
            date_end=date_end,
        )


def test_create_booking_rejects_overlapping_booking(
    user,
    booking_listing,
):
    date_start, date_end = get_booking_dates()

    create_booking(
        tenant=user,
        listing_id=booking_listing.id,
        date_start=date_start,
        date_end=date_end,
    )

    another_user = BookingUser.objects.create_user(
        email="anotheruser@example.com",
        password="TestPassword1!",
        first_name="Another",
        last_name="User",
        phone="+491234567891",
    )

    overlapping_start = date_start + timedelta(days=1)
    overlapping_end = date_end - timedelta(days=1)

    with pytest.raises(ValidationError):
        create_booking(
            tenant=another_user,
            listing_id=booking_listing.id,
            date_start=overlapping_start,
            date_end=overlapping_end,
        )


def test_confirm_booking_changes_status_to_confirmed(
    user,
    booking_listing,
):
    date_start, date_end = get_booking_dates()

    booking = create_booking(
        tenant=user,
        listing_id=booking_listing.id,
        date_start=date_start,
        date_end=date_end,
    )

    confirmed_booking = confirm_booking(
        booking_id=booking.id,
        owner=booking_listing.owner,
    )

    assert confirmed_booking.status == BookingStatus.CONFIRMED


def test_confirm_booking_rejects_non_owner(
    user,
    booking_owner,
    booking_listing,
):
    date_start, date_end = get_booking_dates()

    booking = create_booking(
        tenant=user,
        listing_id=booking_listing.id,
        date_start=date_start,
        date_end=date_end,
    )

    with pytest.raises(ValidationError):
        confirm_booking(
            booking_id=booking.id,
            owner=user,
        )


def test_confirm_booking_rejects_non_pending_booking(
    user,
    booking_listing,
):
    date_start, date_end = get_booking_dates()

    booking = create_booking(
        tenant=user,
        listing_id=booking_listing.id,
        date_start=date_start,
        date_end=date_end,
    )

    booking.status = BookingStatus.CANCELLED
    booking.save(update_fields=["status"])

    with pytest.raises(ValidationError):
        confirm_booking(
            booking_id=booking.id,
            owner=booking_listing.owner,
        )


def test_reject_booking_changes_status_to_rejected(
    user,
    booking_listing,
):
    date_start, date_end = get_booking_dates()

    booking = create_booking(
        tenant=user,
        listing_id=booking_listing.id,
        date_start=date_start,
        date_end=date_end,
    )

    reject_booking(
        booking_id=booking.id,
        owner=booking_listing.owner,
    )

    booking.refresh_from_db()

    assert booking.status == BookingStatus.REJECTED


def test_cancel_booking_changes_status_to_cancelled(
    user,
    booking_listing,
):
    date_start, date_end = get_booking_dates()

    booking = create_booking(
        tenant=user,
        listing_id=booking_listing.id,
        date_start=date_start,
        date_end=date_end,
    )

    cancelled_booking = cancel_booking(
        booking_id=booking.id,
        tenant=user,
    )

    assert cancelled_booking.status == BookingStatus.CANCELLED


def test_cancel_booking_rejects_non_tenant(
    user,
    booking_owner,
    booking_listing,
):
    date_start, date_end = get_booking_dates()

    booking = create_booking(
        tenant=user,
        listing_id=booking_listing.id,
        date_start=date_start,
        date_end=date_end,
    )

    with pytest.raises(ValidationError):
        cancel_booking(
            booking_id=booking.id,
            tenant=booking_owner,
        )


def test_complete_booking_if_finished_changes_status(
    user,
    booking_listing,
):
    date_start = timezone.now() - timedelta(days=3)
    date_end = timezone.now() - timedelta(days=1)

    booking = Booking.objects.create(
        tenant=user,
        listing=booking_listing,
        date_start=date_start,
        date_end=date_end,
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
        status=BookingStatus.CONFIRMED,
    )

    complete_booking_if_finished(booking)

    booking.refresh_from_db()

    assert booking.status == BookingStatus.COMPLETED


def test_complete_booking_if_finished_does_not_change_pending_booking(
    user,
    booking_listing,
):
    date_start = timezone.now() - timedelta(days=3)
    date_end = timezone.now() - timedelta(days=1)

    booking = Booking.objects.create(
        tenant=user,
        listing=booking_listing,
        date_start=date_start,
        date_end=date_end,
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
        status=BookingStatus.PENDING,
    )

    complete_booking_if_finished(booking)

    booking.refresh_from_db()

    assert booking.status == BookingStatus.PENDING


def test_confirm_booking_raises_not_found_error(booking_owner):
    booking_id = "00000000-0000-0000-0000-000000000000"

    with pytest.raises(BookingNotFoundError):
        confirm_booking(
            booking_id=booking_id,
            owner=booking_owner,
        )


def test_reject_booking_raises_not_found_error(booking_owner):
    booking_id = "00000000-0000-0000-0000-000000000000"

    with pytest.raises(BookingNotFoundError):
        reject_booking(
            booking_id=booking_id,
            owner=booking_owner,
        )


def test_cancel_booking_raises_not_found_error(user):
    booking_id = "00000000-0000-0000-0000-000000000000"

    with pytest.raises(BookingNotFoundError):
        cancel_booking(
            booking_id=booking_id,
            tenant=user,
        )