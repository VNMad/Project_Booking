from rest_framework import serializers

from .models import Listing, Photo


class PhotoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Photo
        fields = ["id", "image", "position", "created_at"]
        read_only_fields = ["id", "created_at"]


class ListingSerializer(serializers.ModelSerializer):
    photos = PhotoSerializer(many=True, required=False)
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
            "is_active",
            "deleted_at",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "is_active",
            "deleted_at",
            "created_at",
            "updated_at",
        ]