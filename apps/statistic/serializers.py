from rest_framework import serializers


class ListingRatingSerializer(serializers.Serializer):
    """
    Serializer for public rating statistics of a rental listing.

    Contains the total number of reviews and separate average ratings
    for cleanliness and location.
    """
    listing_id = serializers.UUIDField(help_text="UUID of the rental listing.")
    reviews_count = serializers.IntegerField(help_text="Total number of reviews for this listing.")
    average_cleanliness = serializers.FloatField(allow_null=True, help_text="Average cleanliness rating from 1 to 5.")
    average_location = serializers.FloatField(allow_null=True, help_text="Average location rating from 1 to 5.")


class ListingStatisticsSerializer(ListingRatingSerializer):
    """
    Serializer for extended statistics of a rental listing.

    Includes review statistics inherited from ListingRatingSerializer
    and additional booking statistics.
    """
    bookings_count = serializers.IntegerField(help_text="Total number of bookings for this listing.")
    confirmed_bookings = serializers.IntegerField(help_text="Number of confirmed bookings for this listing.")
    completed_bookings = serializers.IntegerField(help_text="Number of completed bookings for this listing.")