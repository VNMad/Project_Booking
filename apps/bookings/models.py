from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError

from djmoney.models.fields import MoneyField
from simple_history.models import HistoricalRecords

from core.models import BookingStatus, TimeStampedModel, UniqueID
from apps.listings.models import Listing



class Booking(UniqueID, TimeStampedModel):

    tenant = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True,
                               related_name="bookings", verbose_name=_("Tenant"),)
    listing = models.ForeignKey(Listing, on_delete=models.SET_NULL, null=True, related_name="bookings",
                                verbose_name=_("Listing"),)
    date_start = models.DateTimeField(verbose_name=_("Check-in"),)
    date_end = models.DateTimeField(verbose_name=_("Check-out"),)
    snapshot_title = models.CharField(max_length=200, verbose_name=_("Property title"),)
    snapshot_country = models.CharField(max_length=2, verbose_name=_("Country"),)
    snapshot_city = models.CharField(max_length=100, verbose_name=_("City"),)
    snapshot_district = models.CharField(max_length=100, verbose_name=_("District"),)
    snapshot_street = models.CharField(max_length=150, verbose_name=_("Street"),)
    snapshot_house_number = models.CharField(max_length=20, verbose_name=_("House number"),)
    snapshot_apartment_number = models.CharField(max_length=20, verbose_name=_("Apartment number"),)
    snapshot_price_per_night = MoneyField(max_digits=10, decimal_places=2, default_currency="EUR",
                                 verbose_name=_("Price per night"),)
    status = models.CharField(max_length=20, choices=BookingStatus, default=BookingStatus.PENDING,
                              verbose_name=_("Status"),)

    history = HistoricalRecords()

    def clean(self):
        if self.date_start and self.date_end and self.date_start >= self.date_end:
            raise ValidationError({"date_end": _("Check-out must be later than check-in.")})

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    class Meta:
        db_table = "booking"
        verbose_name = _("Booking")
        verbose_name_plural = _("Bookings")
        ordering = ["-created_at"]

        indexes = [
            models.Index(
                fields=["listing", "date_start", "date_end"],
                name="booking_listing_dates_idx",
            ),
            models.Index(
                fields=["tenant", "status"],
                name="booking_tenant_status_idx",
            ),
            models.Index(
                fields=["listing", "status"],
                name="booking_listing_status_idx",
            ),
            models.Index(
                fields=["date_start", "date_end"],
                name="booking_dates_idx",
            ),
        ]

    def __str__(self):
        return f"{self.property_title} - {self.date_start:%Y-%m-%d}"