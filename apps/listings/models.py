from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _
from simple_history.models import HistoricalRecords
from djmoney.models.fields import MoneyField

from core.models import EuropeanCountry, RoomCount, TimeStampedModel, UniqueID


class Listing(UniqueID, TimeStampedModel):

    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True,
                              related_name="listings", verbose_name=_("Owner"),)
    title = models.CharField(max_length=200, verbose_name=_("Title"),)
    description = models.TextField(verbose_name=_("Description"),)
    country = models.CharField(max_length=2, choices=EuropeanCountry, verbose_name=_("Country"),)
    city = models.CharField(max_length=100, verbose_name=_("City"),)
    district = models.CharField(max_length=100, verbose_name=_("District"),)
    street = models.CharField(max_length=150, verbose_name=_("Street"),)
    house_number = models.CharField(max_length=20, verbose_name=_("House number"),)
    apartment_number = models.CharField(max_length=20, verbose_name=_("Apartment number"),)
    price_per_night = MoneyField(max_digits=10, decimal_places=2,
                                 default_currency="EUR", verbose_name=_("Price per night"),)
    rooms = models.CharField(max_length=2, choices=RoomCount, verbose_name=_("Rooms"),)
    is_active = models.BooleanField(default=True, verbose_name=_("Active"),)
    deleted_at = models.DateTimeField(null=True, blank=True, verbose_name=_("Deleted at"),)

    history = HistoricalRecords()

    class Meta:
        db_table = "listing"
        verbose_name = _("Listing")
        verbose_name_plural = _("Listings")
        ordering = ["-created_at"]

        constraints = [
            models.UniqueConstraint(
                fields=[
                    "country",
                    "city",
                    "street",
                    "house_number",
                    "apartment_number",
                ],
                name="unique_listing_address",
            ),
        ]

        indexes = [
            models.Index(
                fields=["country", "city"],
                name="listing_country_city_idx",
            ),
            models.Index(
                fields=["city", "district"],
                name="listing_city_district_idx",
            ),
            models.Index(
                fields=["city", "district", "rooms"],
                name="listing_city_district_room_idx",
            ),
        ]

    def __str__(self):
        return self.title


class Photo(UniqueID, TimeStampedModel):

    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="photos", verbose_name=_("Listing"),)
    image = models.ImageField(upload_to="listings/", verbose_name=_("Image"),)

    class Meta:
        db_table = "listing_photo"
        verbose_name = _("Photo")
        verbose_name_plural = _("Photos")
        ordering = ["created_at"]
        indexes = [
            models.Index(
                fields=["listing", "created_at"],
                name="photo_listing_created_idx",
            ),
        ]

    def __str__(self):
        return f"Photo for {self.listing.title}"