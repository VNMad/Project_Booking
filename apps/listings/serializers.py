from rest_framework import serializers

from .models import Listing


class ListingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Listing
        fields = [
            "id",
            "owner",
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
            "is_active",
            "deleted_at",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "owner",
            "is_active",
            "deleted_at",
            "created_at",
            "updated_at",
        ]