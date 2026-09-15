from datetime import timedelta

from django.utils import timezone
from rest_framework import serializers

from .models import Booking
from core.constants import (BOOKING_MAX_DAYS_AHEAD, BOOKING_CHECK_IN_START, BOOKING_CHECK_IN_END,
                            BOOKING_CHECK_OUT_START, BOOKING_CHECK_OUT_END)


class BookingCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating a new booking.

    The client provides the listing and check-in/check-out dates.
    The tenant, booking status, property snapshot, and tenant snapshot
    are determined by the server.
    """
    class Meta:
        model = Booking
        fields = ["listing", "date_start", "date_end"]
        extra_kwargs = {
            "listing": {"help_text": "Rental listing to be booked."},
            "date_start": {"help_text": ("Check-in date and time. "
                                         "The booking must start in the future and "
                                         "the time must be within the allowed check-in period.")},
            "date_end": {"help_text": ("Check-out date and time. "
                                       "The check-out must be later than the check-in "
                                       "and the time must be within the allowed check-out period.")},
        }

    def validate(self, attrs):
        """
        Validate booking dates and allowed check-in/check-out times.

        The booking must start before it ends, start in the future,
        and not exceed the configured maximum booking horizon.
        """
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
    """
    Serializer for displaying booking information.

    In addition to the booking dates and status, the serializer exposes
    snapshots of the property and tenant information captured when
    the booking was created.
    """
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
        extra_kwargs = {
            "listing": {"help_text": "Rental listing associated with the booking."},
            "date_start": {"help_text": "Check-in date and time."},
            "date_end": {"help_text": "Check-out date and time."},
            "snapshot_title": {"help_text": "Property title captured when the booking was created."},
            "snapshot_country": {"help_text": "Property country captured when the booking was created."},
            "snapshot_city": {"help_text": "Property city captured when the booking was created."},
            "snapshot_district": {"help_text": "Property district captured when the booking was created."},
            "snapshot_street": {"help_text": "Property street captured when the booking was created."},
            "snapshot_house_number": {"help_text": "Property house number captured when the booking was created."},
            "snapshot_apartment_number": {"help_text": (
                                            "Property apartment number captured when the booking was created.")},
            "snapshot_first_name": {"help_text": "Tenant first name captured when the booking was created."},
            "snapshot_last_name": {"help_text": "Tenant last name captured when the booking was created."},
            "snapshot_email": {"help_text": "Tenant email captured when the booking was created."},
            "snapshot_price_per_night": {"help_text": "Price per night captured when the booking was created."},
            "status": {"help_text": "Current status of the booking."},
            "created_at": {"help_text": "Date and time when the booking was created."},
            "updated_at": {"help_text": "Date and time when the booking was last updated."},
        }