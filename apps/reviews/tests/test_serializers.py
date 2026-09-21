import pytest

from apps.reviews.models import Review
from apps.reviews.serializers import (
    ReviewCreateSerializer,
    ReviewSerializer,
)


def test_review_create_serializer_valid_data(completed_booking):
    """
    Check that valid review data passes serializer validation.
    """
    data = {
        "booking": str(completed_booking.id),
        "cleanliness_rating": 5,
        "location_rating": 4,
        "comment": "Very clean apartment and good location.",
    }

    serializer = ReviewCreateSerializer(data=data)

    assert serializer.is_valid() is True
    assert serializer.validated_data["booking"] == completed_booking
    assert serializer.validated_data["cleanliness_rating"] == 5
    assert serializer.validated_data["location_rating"] == 4
    assert serializer.validated_data["comment"] == (
        "Very clean apartment and good location."
    )


@pytest.mark.parametrize(
    "rating",
    [0, 6, -1, 10],
)
def test_review_create_serializer_rejects_invalid_cleanliness_rating(
    completed_booking,
    rating,
):
    """
    Check that invalid cleanliness ratings are rejected.
    """
    data = {
        "booking": str(completed_booking.id),
        "cleanliness_rating": rating,
        "location_rating": 5,
        "comment": "",
    }

    serializer = ReviewCreateSerializer(data=data)

    assert serializer.is_valid() is False
    assert "cleanliness_rating" in serializer.errors


@pytest.mark.parametrize(
    "rating",
    [0, 6, -1, 10],
)
def test_review_create_serializer_rejects_invalid_location_rating(
    completed_booking,
    rating,
):
    """
    Check that invalid location ratings are rejected.
    """
    data = {
        "booking": str(completed_booking.id),
        "cleanliness_rating": 5,
        "location_rating": rating,
        "comment": "",
    }

    serializer = ReviewCreateSerializer(data=data)

    assert serializer.is_valid() is False
    assert "location_rating" in serializer.errors


def test_review_create_serializer_requires_booking():
    """
    Check that booking is required when creating a review.
    """
    data = {
        "cleanliness_rating": 5,
        "location_rating": 4,
        "comment": "Good apartment.",
    }

    serializer = ReviewCreateSerializer(data=data)

    assert serializer.is_valid() is False
    assert "booking" in serializer.errors


def test_review_create_serializer_requires_cleanliness_rating(completed_booking):
    """
    Check that cleanliness rating is required.
    """
    data = {
        "booking": str(completed_booking.id),
        "location_rating": 4,
        "comment": "Good apartment.",
    }

    serializer = ReviewCreateSerializer(data=data)

    assert serializer.is_valid() is False
    assert "cleanliness_rating" in serializer.errors


def test_review_create_serializer_requires_location_rating(completed_booking):
    """
    Check that location rating is required.
    """
    data = {
        "booking": str(completed_booking.id),
        "cleanliness_rating": 5,
        "comment": "Good apartment.",
    }

    serializer = ReviewCreateSerializer(data=data)

    assert serializer.is_valid() is False
    assert "location_rating" in serializer.errors


def test_review_create_serializer_allows_missing_comment(completed_booking):
    """
    Check that comment is optional.
    """
    data = {
        "booking": str(completed_booking.id),
        "cleanliness_rating": 5,
        "location_rating": 4,
    }

    serializer = ReviewCreateSerializer(data=data)

    assert serializer.is_valid() is True


def test_review_serializer_returns_review_data(completed_booking):
    """
    Check that ReviewSerializer returns all expected review fields.
    """
    review = Review.objects.create(
        booking=completed_booking,
        cleanliness_rating=5,
        location_rating=4,
        comment="Great stay.",
    )

    serializer = ReviewSerializer(review)

    assert serializer.data["id"] == str(review.id)
    assert serializer.data["booking"] == review.booking_id
    assert serializer.data["cleanliness_rating"] == 5
    assert serializer.data["location_rating"] == 4
    assert serializer.data["comment"] == "Great stay."
    assert serializer.data["created_at"] is not None
    assert serializer.data["updated_at"] is not None


@pytest.mark.parametrize(
    "field_name",
    [
        "id",
        "booking",
        "created_at",
        "updated_at",
    ],
)
def test_review_serializer_read_only_fields(field_name):
    """
    Check that system-managed review fields are read-only.
    """
    serializer = ReviewSerializer()

    assert serializer.fields[field_name].read_only is True