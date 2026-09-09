import uuid

from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _


class UniqueID(models.Model):
    id = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4, verbose_name=_("UUID id"))

    class Meta:
        abstract = True


class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Created at"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Updated at"))

    class Meta:
        abstract = True


class RoomCount(models.TextChoices):
    ONE = "1", _("1")
    TWO = "2", _("2")
    THREE = "3", _("3")
    FOUR = "4", _("4")
    FIVE = "5", _("5")
    FIVE_PLUS = "5+", _("5+")


class BookingStatus(models.TextChoices):
    PENDING = "pending", _("Pending")
    CONFIRMED = "confirmed", _("Confirmed")
    REJECTED = "rejected", _("Rejected")
    CANCELLED = "cancelled", _("Cancelled")
    COMPLETED = "completed", _("Completed")


class EuropeanCountry(models.TextChoices):
    ALBANIA = "AL", _("Albania")
    ANDORRA = "AD", _("Andorra")
    ARMENIA = "AM", _("Armenia")
    AUSTRIA = "AT", _("Austria")
    AZERBAIJAN = "AZ", _("Azerbaijan")
    BELARUS = "BY", _("Belarus")
    BELGIUM = "BE", _("Belgium")
    BOSNIA_AND_HERZEGOVINA = "BA", _("Bosnia and Herzegovina")
    BULGARIA = "BG", _("Bulgaria")
    CROATIA = "HR", _("Croatia")
    CYPRUS = "CY", _("Cyprus")
    CZECHIA = "CZ", _("Czechia")
    DENMARK = "DK", _("Denmark")
    ESTONIA = "EE", _("Estonia")
    FINLAND = "FI", _("Finland")
    FRANCE = "FR", _("France")
    GEORGIA = "GE", _("Georgia")
    GERMANY = "DE", _("Germany")
    GREECE = "GR", _("Greece")
    HUNGARY = "HU", _("Hungary")
    ICELAND = "IS", _("Iceland")
    IRELAND = "IE", _("Ireland")
    ITALY = "IT", _("Italy")
    KOSOVO = "XK", _("Kosovo")
    LATVIA = "LV", _("Latvia")
    LIECHTENSTEIN = "LI", _("Liechtenstein")
    LITHUANIA = "LT", _("Lithuania")
    LUXEMBOURG = "LU", _("Luxembourg")
    MALTA = "MT", _("Malta")
    MOLDOVA = "MD", _("Moldova")
    MONACO = "MC", _("Monaco")
    MONTENEGRO = "ME", _("Montenegro")
    NETHERLANDS = "NL", _("Netherlands")
    NORTH_MACEDONIA = "MK", _("North Macedonia")
    NORWAY = "NO", _("Norway")
    POLAND = "PL", _("Poland")
    PORTUGAL = "PT", _("Portugal")
    ROMANIA = "RO", _("Romania")
    RUSSIA = "RU", _("Russia")
    SAN_MARINO = "SM", _("San Marino")
    SERBIA = "RS", _("Serbia")
    SLOVAKIA = "SK", _("Slovakia")
    SLOVENIA = "SI", _("Slovenia")
    SPAIN = "ES", _("Spain")
    SWEDEN = "SE", _("Sweden")
    SWITZERLAND = "CH", _("Switzerland")
    TURKEY = "TR", _("Turkey")
    UKRAINE = "UA", _("Ukraine")
    UNITED_KINGDOM = "GB", _("United Kingdom")
    VATICAN_CITY = "VA", _("Vatican City")



