from rest_framework import serializers


class ListingRatingSerializer(serializers.Serializer):
    listing_id = serializers.UUIDField(help_text="UUID of the rental listing.")
    reviews_count = serializers.IntegerField(help_text="Total number of reviews for this listing.")
    average_cleanliness = serializers.FloatField(allow_null=True, help_text="Average cleanliness rating from 1 to 5.")
    average_location = serializers.FloatField(allow_null=True, help_text="Average location rating from 1 to 5.")


class ListingStatisticsSerializer(ListingRatingSerializer):
    bookings_count = serializers.IntegerField(help_text="Total number of bookings for this listing.")
    confirmed_bookings = serializers.IntegerField(help_text="Number of confirmed bookings for this listing.")
    completed_bookings = serializers.IntegerField(help_text="Number of completed bookings for this listing.")