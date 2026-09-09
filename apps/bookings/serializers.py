from datetime import time, timedelta

from django.utils import timezone
from rest_framework import serializers

from .models import Booking


class BookingCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Booking
        fields = ["listing", "date_start", "date_end",]

    def validate(self, attrs):
        date_start = attrs["date_start"]
        date_end = attrs["date_end"]

        now = timezone.now()
        max_date = now + timedelta(days=365)

        if date_start >= date_end:
            raise serializers.ValidationError({"date_end": ("Check-out must be later than check-in.")})

        if date_start < now:
            raise serializers.ValidationError({"date_start": ("Booking must start in the future.")})

        if date_end > max_date:
            raise serializers.ValidationError({"date_end": ("Booking cannot be more than 1 year in the future.")})

        local_start = timezone.localtime(date_start)
        local_end = timezone.localtime(date_end)

        if local_start.time() != time(14, 0):
            raise serializers.ValidationError({"date_start": ("Check-in time must be exactly 14:00.")})

        if local_end.time() != time(11, 0):
            raise serializers.ValidationError({"date_end": ("Check-out time must be exactly 11:00.")})

        return attrs


class BookingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Booking
        fields = [
            "id",
            "tenant",
            "listing",
            "date_start",
            "date_end",
            "snapshot_title",
            "snapshot_country",
            "snapshot_city",
            "snapshot_district",
            "snapshot_street",
            "snapshot_house_number",
            "snapshot_apartment_number",
            "snapshot_price_per_night",
            "status",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "tenant",
            "snapshot_title",
            "snapshot_country",
            "snapshot_city",
            "snapshot_district",
            "snapshot_street",
            "snapshot_house_number",
            "snapshot_apartment_number",
            "snapshot_price_per_night",
            "status",
            "created_at",
            "updated_at",
        ]