import pytest
from django.core.exceptions import ValidationError

from apps.reviews.models import Review


def test_review_creation(completed_booking):
    """
    Check that a review is created with the expected values.
    """
    review = Review.objects.create(
        booking=completed_booking,
        cleanliness_rating=5,
        location_rating=4,
        comment="Very clean apartment in a great location.",
    )

    assert review.booking == completed_booking
    assert review.cleanliness_rating == 5
    assert review.location_rating == 4
    assert review.comment == "Very clean apartment in a great location."


def test_review_has_uuid_and_timestamps(completed_booking):
    """
    Check that a review receives an ID and timestamps.
    """
    review = Review.objects.create(
        booking=completed_booking,
        cleanliness_rating=5,
        location_rating=5,
    )

    assert review.id is not None
    assert review.created_at is not None
    assert review.updated_at is not None


def test_review_str(completed_booking):
    """
    Check the string representation of a review.
    """
    review = Review.objects.create(
        booking=completed_booking,
        cleanliness_rating=5,
        location_rating=5,
    )

    assert str(review) == f"Review for {completed_booking.id}"


def test_review_allows_empty_comment(completed_booking):
    """
    Check that the comment field can be empty.
    """
    review = Review(
        booking=completed_booking,
        cleanliness_rating=5,
        location_rating=5,
        comment="",
    )

    review.full_clean()


@pytest.mark.parametrize(
    "rating",
    [1, 2, 3, 4, 5],
)
def test_review_accepts_valid_cleanliness_rating(completed_booking, rating):
    """
    Check that cleanliness ratings from 1 to 5 are accepted.
    """
    review = Review(
        booking=completed_booking,
        cleanliness_rating=rating,
        location_rating=5,
    )

    review.full_clean()


@pytest.mark.parametrize(
    "rating",
    [0, 6, -1, 10],
)
def test_review_rejects_invalid_cleanliness_rating(completed_booking, rating):
    """
    Check that cleanliness ratings outside 1-5 are rejected.
    """
    review = Review(
        booking=completed_booking,
        cleanliness_rating=rating,
        location_rating=5,
    )

    with pytest.raises(ValidationError):
        review.full_clean()


@pytest.mark.parametrize(
    "rating",
    [1, 2, 3, 4, 5],
)
def test_review_accepts_valid_location_rating(completed_booking, rating):
    """
    Check that location ratings from 1 to 5 are accepted.
    """
    review = Review(
        booking=completed_booking,
        cleanliness_rating=5,
        location_rating=rating,
    )

    review.full_clean()


@pytest.mark.parametrize(
    "rating",
    [0, 6, -1, 10],
)
def test_review_rejects_invalid_location_rating(completed_booking, rating):
    """
    Check that location ratings outside 1-5 are rejected.
    """
    review = Review(
        booking=completed_booking,
        cleanliness_rating=5,
        location_rating=rating,
    )

    with pytest.raises(ValidationError):
        review.full_clean()


def test_review_allows_only_one_review_per_booking(completed_booking):
    """
    Check that only one review can be associated with a booking.
    """
    Review.objects.create(
        booking=completed_booking,
        cleanliness_rating=5,
        location_rating=5,
    )

    duplicate_review = Review(
        booking=completed_booking,
        cleanliness_rating=4,
        location_rating=4,
    )

    with pytest.raises(ValidationError):
        duplicate_review.full_clean()