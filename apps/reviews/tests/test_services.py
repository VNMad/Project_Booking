import pytest
from django.core.exceptions import ValidationError

from apps.reviews.models import Review
from apps.reviews.services import create_review
from core.models import BookingStatus


def test_create_review_creates_review(user, completed_booking):
    """
    Check that the tenant can create a review for a completed booking.
    """
    review = create_review(
        booking=completed_booking,
        user=user,
        cleanliness_rating=5,
        location_rating=4,
        comment="Very clean apartment and great location.",
    )

    assert isinstance(review, Review)
    assert review.booking == completed_booking
    assert review.cleanliness_rating == 5
    assert review.location_rating == 4
    assert review.comment == "Very clean apartment and great location."


def test_create_review_saves_review_to_database(user, completed_booking):
    """
    Check that create_review saves the review to the database.
    """
    review = create_review(
        booking=completed_booking,
        user=user,
        cleanliness_rating=5,
        location_rating=5,
        comment="Excellent stay.",
    )

    assert Review.objects.filter(id=review.id).exists() is True


def test_create_review_rejects_non_tenant(
    booking_owner,
    completed_booking,
):
    """
    Check that a user who did not make the booking cannot leave a review.
    """
    with pytest.raises(ValidationError):
        create_review(
            booking=completed_booking,
            user=booking_owner,
            cleanliness_rating=5,
            location_rating=5,
            comment="Unauthorized review.",
        )


def test_create_review_rejects_non_completed_booking(
    user,
    completed_booking,
):
    """
    Check that a review cannot be created for a booking
    that is not completed.
    """
    completed_booking.status = BookingStatus.PENDING
    completed_booking.save(update_fields=["status"])

    with pytest.raises(ValidationError):
        create_review(
            booking=completed_booking,
            user=user,
            cleanliness_rating=5,
            location_rating=4,
            comment="Booking is not completed.",
        )


def test_create_review_completes_finished_confirmed_booking(
    user,
    completed_booking,
):
    """
    Check that a finished confirmed booking is automatically
    changed to completed before the review is created.
    """
    completed_booking.status = BookingStatus.CONFIRMED
    completed_booking.save(update_fields=["status"])

    review = create_review(
        booking=completed_booking,
        user=user,
        cleanliness_rating=5,
        location_rating=5,
        comment="Great stay.",
    )

    completed_booking.refresh_from_db()

    assert completed_booking.status == BookingStatus.COMPLETED
    assert review.booking == completed_booking


def test_create_review_rejects_duplicate_review(
    user,
    completed_booking,
):
    """
    Check that only one review can be created for a booking.
    """
    create_review(
        booking=completed_booking,
        user=user,
        cleanliness_rating=5,
        location_rating=5,
        comment="First review.",
    )

    with pytest.raises(ValidationError):
        create_review(
            booking=completed_booking,
            user=user,
            cleanliness_rating=4,
            location_rating=4,
            comment="Second review.",
        )


def test_create_review_allows_empty_comment(
    user,
    completed_booking,
):
    """
    Check that a review can be created without a text comment.
    """
    review = create_review(
        booking=completed_booking,
        user=user,
        cleanliness_rating=5,
        location_rating=4,
        comment="",
    )

    assert review.comment == ""