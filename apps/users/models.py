from django.contrib.auth.models import AbstractUser, UserManager
from django.db import models
from django.utils.translation import gettext_lazy as _
from core.models import TimeStampedModel, UniqueID


class BookingUserManager(UserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("Email is required")

        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        return self.create_user(email=email, password=password, **extra_fields)

class Booking_User(TimeStampedModel, AbstractUser):
    username = None

    first_name = models.CharField(max_length=25, verbose_name=_("First name"))
    last_name = models.CharField(max_length=25, verbose_name=_("Last name"))
    email = models.EmailField(unique=True, verbose_name=_("Email"))
    phone = models.CharField(max_length=20, verbose_name=_("Phone"))

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = BookingUserManager()

    def __str__(self):
        return self.email

    class Meta:
        db_table = "booking_user"
        verbose_name = _("Booking user")
        verbose_name_plural = _("Booking users")
        ordering = ["-date_joined"]