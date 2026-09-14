from datetime import timedelta

from django.utils import timezone
from rest_framework import serializers

from .models import Booking
from core.constants import (BOOKING_MAX_DAYS_AHEAD, BOOKING_CHECK_IN_START, BOOKING_CHECK_IN_END,
                            BOOKING_CHECK_OUT_START, BOOKING_CHECK_OUT_END)


class BookingCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Booking
        fields = ["listing", "date_start", "date_end",]

    def validate(self, attrs):
        date_start = attrs["date_start"]
        date_end = attrs["date_end"]

        now = timezone.now()
        max_date = now + timedelta(days=BOOKING_MAX_DAYS_AHEAD)

        if date_start >= date_end:
            raise serializers.ValidationError({"date_end": "Check-out must be later than check-in."})
        if date_start < now:
            raise serializers.ValidationError({"date_start": "Booking must start in the future."})
        if date_end > max_date:
            raise serializers.ValidationError({"date_end":
                                        f"Booking cannot be more than {BOOKING_MAX_DAYS_AHEAD} days in the future."})

        local_start = timezone.localtime(date_start)
        local_end = timezone.localtime(date_end)
        if not (BOOKING_CHECK_IN_START <= local_start.time() <= BOOKING_CHECK_IN_END):
            in_start = BOOKING_CHECK_IN_START.strftime("%H:%M")
            in_end = BOOKING_CHECK_IN_END.strftime("%H:%M")
            raise serializers.ValidationError({"date_start": f"Check-in time must be between {in_start} and {in_end}"})
        if not (BOOKING_CHECK_OUT_START <= local_end.time() <= BOOKING_CHECK_OUT_END):
            out_start = BOOKING_CHECK_OUT_START.strftime("%H:%M")
            out_end = BOOKING_CHECK_OUT_END.strftime("%H:%M")
            raise serializers.ValidationError({"date_end": f"Check-out time must be between {out_start} and {out_end}"})
        return attrs


class BookingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Booking
        fields = [
            "id",
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
            "snapshot_first_name",
            "snapshot_last_name",
            "snapshot_email",
            "snapshot_price_per_night",
            "status",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "snapshot_title",
            "snapshot_country",
            "snapshot_city",
            "snapshot_district",
            "snapshot_street",
            "snapshot_house_number",
            "snapshot_apartment_number",
            "snapshot_first_name",
            "snapshot_last_name",
            "snapshot_email",
            "snapshot_price_per_night",
            "status",
            "created_at",
            "updated_at",
        ]