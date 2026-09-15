from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from core.models import BookingStatus
from .models import Review
from apps.bookings.services import complete_booking_if_finished


def create_review(*, booking, user, cleanliness_rating, location_rating, comment):
    """
    Create a review for a completed booking.

    The function verifies that the authenticated user is the tenant
    who made the booking. If the booking has reached its end time,
    it is automatically marked as COMPLETED.

    A review can only be created for a completed booking and only one
    review can be associated with each booking.
    """
    if booking.tenant_id != user.id:
        raise ValidationError(_("Only the tenant who made the booking can leave a review."))
    booking = complete_booking_if_finished(booking)

    if booking.status != BookingStatus.COMPLETED:
        raise ValidationError(_("Review can only be created for a completed booking."))

    if hasattr(booking, "review"):
        raise ValidationError(_("A review for this booking already exists."))

    review = Review.objects.create(booking=booking, cleanliness_rating=cleanliness_rating,
                                   location_rating=location_rating, comment=comment)
    return review
