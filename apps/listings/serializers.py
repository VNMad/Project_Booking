from rest_framework import serializers

from .models import Listing, Photo
from core.constants import LISTING_MAX_PHOTOS


class PhotoSerializer(serializers.ModelSerializer):
    """
    Serializer for listing photos.
    Each photo belongs to a listing and has a position that determines
    its order in the listing's photo collection.
    """
    position = serializers.IntegerField(min_value=1, help_text="Photo position in the listing. Starts from 1.")
    class Meta:
        model = Photo
        fields = ["id", "listing", "image", "position", "created_at"]
        read_only_fields = ["id", "created_at"]
        extra_kwargs = {
            "listing": {"help_text": "Listing to which the photo belongs."},
            "image": {"help_text": "Image file of the rental property."},
            "created_at": {"help_text": "Date and time when the photo was uploaded."},
        }


class ListingSerializer(serializers.ModelSerializer):
    """
    Serializer for rental listing data.
    Provides listing details, property photos, and calculated review
    statistics. Review statistics are read-only and are calculated
    from the reviews associated with the listing.
    """
    photos = PhotoSerializer(many=True, required=False,
                             help_text=(f"Photos of the listing. A listing can contain up to "
                                        f"{LISTING_MAX_PHOTOS} photos."))
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
        extra_kwargs = {
            "title": {"help_text": "Title of the rental listing."},
            "description": {"help_text": "Detailed description of the rental property."},
            "country": {"help_text": "European country where the property is located."},
            "city": {"help_text": "City where the property is located."},
            "district": {"help_text": "District or neighborhood where the property is located."},
            "street": {"help_text": "Street address of the property."},
            "house_number": {"help_text": "House number of the property."},
            "apartment_number": {"help_text": "Apartment number of the property."},
            "price_per_night": {"help_text": "Rental price per night."},
            "rooms": {"help_text": "Number of rooms in the rental property."},
            "is_active": {"help_text": "Indicates whether the listing is currently active."},
            "deleted_at": {"help_text": ("Date and time when the listing was soft-deleted. "
                                         "Null for active listings.")},
            "created_at": {"help_text": "Date and time when the listing was created."},
            "updated_at": {"help_text": "Date and time when the listing was last updated."},
        }

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