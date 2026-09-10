from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _
from simple_history.models import HistoricalRecords

from core.models import TimeStampedModel, UniqueID
from apps.bookings.models import Booking


class Review(UniqueID, TimeStampedModel):

    booking = models.OneToOneField(Booking, on_delete=models.CASCADE, related_name="review", verbose_name=_("Booking"),)
    cleanliness_rating = models.PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5),],
                                                          verbose_name=_("Cleanliness rating"),)
    location_rating = models.PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5),],
                                                       verbose_name=_("Location rating"),)
    comment = models.TextField(blank=True, verbose_name=_("Comment"),)

    history = HistoricalRecords()

    class Meta:
        db_table = "review"
        verbose_name = _("Review")
        verbose_name_plural = _("Reviews")
        ordering = ["-created_at"]

        indexes = [
            models.Index(
                fields=["location_rating"],
                name="review_location_rating_at_idx",
            ),
        ]

    def __str__(self):
        return f"Review for {self.booking_id}"