from rest_framework import serializers

from .models import Listing, Photo
from core.constants import LISTING_MAX_PHOTOS


class PhotoSerializer(serializers.ModelSerializer):
    position = serializers.IntegerField(min_value=1)
    class Meta:
        model = Photo
        fields = ["id", "listing", "image", "position", "created_at"]
        read_only_fields = ["id", "created_at"]


class ListingSerializer(serializers.ModelSerializer):
    photos = PhotoSerializer(many=True, required=False)
    reviews_count = serializers.IntegerField(read_only=True, help_text="Total number of reviews for this listing.")
    average_cleanliness = serializers.FloatField(read_only=True, allow_null=True,
                                                 help_text="Average cleanliness rating from 1 to 5.")

    average_location = serializers.FloatField(read_only=True, allow_null=True,
                                              help_text="Average location rating from 1 to 5.")
    class Meta:
        model = Listing
        fields = [
            "id",
            "title",
            "description",
            "country",
            "city",
            "district",
            "street",
            "house_number",
            "apartment_number",
            "price_per_night",
            "rooms",
            "photos",
            "reviews_count",
            "average_cleanliness",
            "average_location",
            "is_active",
            "deleted_at",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "reviews_count",
            "average_cleanliness",
            "average_location",
            "is_active",
            "deleted_at",
            "created_at",
            "updated_at",
        ]

    def validate_photos(self, value):
        incoming_count = len(value)

        if self.instance:
            existing_count = self.instance.photos.count()
            total_count = existing_count + incoming_count
        else:
            total_count = incoming_count

        if total_count > LISTING_MAX_PHOTOS:
            raise serializers.ValidationError(
                f"A listing cannot have more than {LISTING_MAX_PHOTOS} photos in total. "
                f"Current total would be {total_count}."
            )
        return value