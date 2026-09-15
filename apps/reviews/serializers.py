from rest_framework import serializers
from .models import Review


class ReviewCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating a review after completing a booking.

    The booking and rating values are provided by the user.
    The review owner is determined from the authenticated user.
    """
    class Meta:
        model = Review
        fields = [
            "booking",
            "cleanliness_rating",
            "location_rating",
            "comment",
        ]
        extra_kwargs = {
            "booking": {"help_text": "Booking for which the review is being created."},
            "cleanliness_rating": {"help_text": "Cleanliness rating of the property from 1 to 5."},
            "location_rating": {"help_text": "Location rating of the property from 1 to 5."},
            "comment": {"help_text": "Optional comment about the rental experience."},
        }

class ReviewSerializer(serializers.ModelSerializer):
    """
    Serializer for displaying review information.

    The booking, review ID, and timestamps are read-only.
    Rating values and the optional comment are returned as review data.
    """

    class Meta:
        model = Review
        fields = [
            "id",
            "booking",
            "cleanliness_rating",
            "location_rating",
            "comment",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "booking",
            "created_at",
            "updated_at",
        ]
        extra_kwargs = {
            "id": {"help_text": "Unique UUID identifier of the review."},
            "booking": {"help_text": "Booking associated with this review."},
            "cleanliness_rating": {"help_text": "Cleanliness rating of the property from 1 to 5."},
            "location_rating": {"help_text": "Location rating of the property from 1 to 5."},
            "comment": {"help_text": "Optional comment about the rental experience."},
            "created_at": {"help_text": "Date and time when the review was created."},
            "updated_at": {"help_text": "Date and time when the review was last updated."},
        }