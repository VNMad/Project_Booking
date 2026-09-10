from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils.translation import gettext_lazy as _

from core.models import BookingStatus
from apps.listings.models import Listing

from .models import Booking


def create_booking(*, tenant, listing_id, date_start, date_end):
    with transaction.atomic():
        listing = Listing.objects.select_for_update().get(pk=listing_id)

        if not listing.is_active:
            raise ValidationError(_("This listing is not active."))

        if listing.deleted_at is not None:
            raise ValidationError(_("This listing has been deleted."))

        booking_exists = Booking.objects.filter(
            listing=listing, status__in=[BookingStatus.PENDING, BookingStatus.CONFIRMED],
            date_start__lt=date_end, date_end__gt=date_start).exists()

        if booking_exists:
            raise ValidationError(_("The listing is already booked for these dates."))

        booking = Booking.objects.create(
            tenant=tenant,
            listing=listing,
            date_start=date_start,
            date_end=date_end,
            snapshot_title=listing.title,
            snapshot_country=listing.country,
            snapshot_city=listing.city,
            snapshot_district=listing.district,
            snapshot_street=listing.street,
            snapshot_house_number=listing.house_number,
            snapshot_apartment_number=listing.apartment_number,
            snapshot_first_name=tenant.first_name,
            snapshot_last_name=tenant.last_name,
            snapshot_email=tenant.email,
            snapshot_price_per_night=listing.price_per_night,
            status=BookingStatus.PENDING,
        )

        return booking