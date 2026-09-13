from datetime import timedelta
from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from core.models import BookingStatus
from apps.listings.models import Listing

from .models import Booking


class BookingNotFoundError(Exception):
    pass


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


def confirm_booking(*, booking_id, owner):
    try:
        booking = Booking.objects.select_related("listing").get(pk=booking_id)
    except Booking.DoesNotExist:
        raise BookingNotFoundError(_("Booking does not exist."))

    if booking.listing.owner_id != owner.id:
        raise ValidationError(_("Only the listing owner can confirm this booking."))

    if booking.status != BookingStatus.PENDING:
        raise ValidationError(_("Only pending bookings can be confirmed."))

    booking.status = BookingStatus.CONFIRMED
    booking.save(update_fields=["status", "updated_at"])

    return booking


def reject_booking(*, booking_id, owner):
    try:
        booking = Booking.objects.select_related("listing").get(pk=booking_id)
    except Booking.DoesNotExist:
        raise BookingNotFoundError(_("Booking does not exist."))

    if booking.listing.owner_id != owner.id:
        raise ValidationError(_("Only the listing owner can reject this booking."))

    if booking.status != BookingStatus.PENDING:
        raise ValidationError(_("Only pending bookings can be rejected."))

    booking.status = BookingStatus.REJECTED
    booking.save(update_fields=["status", "updated_at"])

    return


def cancel_booking(*, booking_id, tenant):
    try:
        booking = Booking.objects.select_related("listing").get(pk=booking_id)
    except Booking.DoesNotExist:
        raise BookingNotFoundError(_("Booking does not exist."))

    if booking.tenant_id != tenant.id:
        raise ValidationError(_("Only the tenant who created the booking can cancel it."))

    if booking.status != BookingStatus.PENDING:
        raise ValidationError(_("Only pending bookings can be cancelled."))

    now = timezone.now()
    cancellation_deadline = booking.date_start - timedelta(days=1)

    if now > cancellation_deadline:
        raise ValidationError(_("Booking can only be cancelled at least 24 hours before check-in."))

    booking.status = BookingStatus.CANCELLED
    booking.save(update_fields=["status", "updated_at"])

    return booking