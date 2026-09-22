from datetime import datetime, time, timedelta

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from djmoney.money import Money
from faker import Faker
from simple_history.utils import bulk_create_with_history

from apps.bookings.models import Booking
from apps.listings.models import Listing
from apps.reviews.models import Review
from core.models import BookingStatus, RoomCount


DEMO_PREFIX = "[DEMO]"

DEMO_USERS = (
    {
        "email": "owner@admin.com",
        "first_name": "Owner",
        "last_name": "Owner One",
        "phone": "+491111111111",
        "is_staff": True,
        "is_superuser": True,
    },
    {
        "email": "tenant@admin.com",
        "first_name": "Tenant",
        "last_name": "Tenant One",
        "phone": "+492222222222",
        "is_staff": False,
        "is_superuser": False,
    },
    {
        "email": "tenant2@admin.com",
        "first_name": "Tenant",
        "last_name": "Tenant Two",
        "phone": "+493333333333",
        "is_staff": False,
        "is_superuser": False,
    },
    {
        "email": "tenant3@admin.com",
        "first_name": "Tenant",
        "last_name": "Tenant Three",
        "phone": "+494444444444",
        "is_staff": False,
        "is_superuser": False,
    },
)


class Command(BaseCommand):
    """
    Create demo data for local development and presentations.
    """

    help = (
        "Creates demo users, listings, bookings and reviews "
        "for development and presentations."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--count",
            type=int,
            default=20,
            help="Number of demo listings to create. Default: 20.",
        )

    @transaction.atomic
    def handle(self, *args, **options):
        count = options["count"]

        if count < 4:
            self.stderr.write(
                self.style.ERROR(
                    "Count must be at least 4."
                )
            )
            return

        fake = Faker("de_DE")
        Faker.seed(2026)

        password = settings.DEMO_USER_PASSWORD

        self.stdout.write(
            "Removing previously generated demo data..."
        )

        self._clear_demo_data()

        self.stdout.write(
            "Creating demo users..."
        )

        users = self._create_users(password)

        self.stdout.write(
            f"Creating {count} listings..."
        )

        listings = self._create_listings(
            fake=fake,
            users=users,
            count=count,
        )

        self.stdout.write(
            f"Creating {count} bookings..."
        )

        bookings = self._create_bookings(
            listings=listings,
            users=users,
        )

        self.stdout.write(
            "Creating reviews for completed bookings..."
        )

        reviews_count = self._create_reviews(
            fake=fake,
            bookings=bookings,
        )

        self._deactivate_demo_listings(listings)

        self.stdout.write("")
        self.stdout.write(
            self.style.SUCCESS(
                "Demo data created successfully."
            )
        )

        self.stdout.write(
            f"Users: {len(users)}"
        )
        self.stdout.write(
            f"Listings: {len(listings)}"
        )
        self.stdout.write(
            f"Bookings: {len(bookings)}"
        )
        self.stdout.write(
            f"Reviews: {reviews_count}"
        )

        self.stdout.write("")
        self.stdout.write(
            "Demo users:"
        )

        for email in users:
            self.stdout.write(
                f"  - {email}"
            )

        self.stdout.write("")
        self.stdout.write(
            "Password is taken from DEMO_USER_PASSWORD."
        )

    def _clear_demo_data(self):
        """
        Remove only records created by this command.

        Existing real/test data that does not use the demo
        prefix is not touched.
        """
        demo_bookings = Booking.objects.filter(
            snapshot_title__startswith=DEMO_PREFIX,
        )

        Review.objects.filter(
            booking__in=demo_bookings,
        ).delete()

        demo_bookings.delete()

        Listing.objects.filter(
            title__startswith=DEMO_PREFIX,
        ).delete()

    def _create_users(self, password):
        """
        Create or update the four demo users.

        The owner account is also a superuser so it can be used
        during the Django Admin presentation.
        """
        User = get_user_model()

        users = {}

        for user_data in DEMO_USERS:
            email = user_data["email"]

            user, _ = User.objects.update_or_create(
                email=email,
                defaults={
                    "first_name": user_data["first_name"],
                    "last_name": user_data["last_name"],
                    "phone": user_data["phone"],
                    "is_active": True,
                    "is_staff": user_data["is_staff"],
                    "is_superuser": user_data["is_superuser"],
                },
            )

            user.set_password(password)
            user.save()

            users[email] = user

        return users

    def _create_listings(
        self,
        fake,
        users,
        count,
    ):
        """
        Create demo listings.

        Most listings belong to owner@admin.com.
        The last two belong to tenant2@admin.com so that
        owner@admin.com can also have personal bookings.
        """
        owner = users["owner@admin.com"]
        tenant2 = users["tenant2@admin.com"]

        listings = []

        for index in range(count):
            if index >= count - 2:
                listing_owner = tenant2
            else:
                listing_owner = owner

            city = fake.city()
            street = fake.street_name()

            rooms = fake.random_element(
                elements=tuple(RoomCount.values)
            )

            price = 70 + (index * 7)

            listing = Listing.objects.create(
                owner=listing_owner,
                title=(
                    f"{DEMO_PREFIX} "
                    f"Apartment {index + 1} in {city}"
                ),
                description=fake.paragraph(
                    nb_sentences=4
                ),
                country="DE",
                city=city,
                district=f"District {(index % 5) + 1}",
                street=street,
                house_number=str(index + 10),
                apartment_number=str(index + 1),
                price_per_night=Money(
                    price,
                    "EUR",
                ),
                rooms=rooms,
                is_active=True,
            )

            listings.append(listing)

        return listings

    def _create_bookings(
        self,
        listings,
        users,
    ):
        """
        Create one booking for every demo listing.

        Different statuses and dates are used so that the
        presentation contains active, past, cancelled,
        rejected and completed bookings.
        """
        owner = users["owner@admin.com"]

        tenants = (
            users["tenant@admin.com"],
            users["tenant2@admin.com"],
            users["tenant3@admin.com"],
        )

        booking_patterns = (
            (
                BookingStatus.PENDING,
                5,
                7,
            ),
            (
                BookingStatus.CONFIRMED,
                10,
                12,
            ),
            (
                BookingStatus.CANCELLED,
                -15,
                -13,
            ),
            (
                BookingStatus.REJECTED,
                -12,
                -10,
            ),
            (
                BookingStatus.COMPLETED,
                -7,
                -5,
            ),
        )

        bookings = []

        for index, listing in enumerate(listings):
            # The last two listings belong to tenant2.
            # owner@admin.com books them so that the owner
            # also has records in "My bookings".
            if listing.owner_id != owner.id:
                tenant = owner
            else:
                tenant = tenants[index % len(tenants)]

            status_value, start_days, end_days = (
                booking_patterns[
                    index % len(booking_patterns)
                ]
            )

            booking = Booking(
                tenant=tenant,
                listing=listing,

                date_start=self._make_datetime(
                    days=start_days,
                    hour=14,
                ),
                date_end=self._make_datetime(
                    days=end_days,
                    hour=11,
                ),

                snapshot_title=listing.title,
                snapshot_country=listing.country,
                snapshot_city=listing.city,
                snapshot_district=listing.district,
                snapshot_street=listing.street,
                snapshot_house_number=(
                    listing.house_number
                ),
                snapshot_apartment_number=(
                    listing.apartment_number
                ),

                snapshot_first_name=tenant.first_name,
                snapshot_last_name=tenant.last_name,
                snapshot_email=tenant.email,

                snapshot_price_per_night=(
                    listing.price_per_night
                ),

                status=status_value,
            )

            bookings.append(booking)

        # We deliberately use bulk_create_with_history here.
        #
        # Booking post_save signals send notification emails.
        # During database seeding we do not want to send 20
        # real emails, especially after deployment to AWS.
        #
        # bulk_create_with_history creates the records and their
        # django-simple-history entries without triggering
        # normal save signals.
        bulk_create_with_history(
            bookings,
            Booking,
            batch_size=100,
        )

        return bookings

    def _create_reviews(
        self,
        fake,
        bookings,
    ):
        """
        Create reviews only for completed bookings.
        """
        reviews_count = 0

        for booking in bookings:
            if booking.status != BookingStatus.COMPLETED:
                continue

            Review.objects.create(
                booking=booking,
                cleanliness_rating=fake.random_int(
                    min=3,
                    max=5,
                ),
                location_rating=fake.random_int(
                    min=3,
                    max=5,
                ),
                comment=fake.sentence(
                    nb_words=12,
                ),
            )

            reviews_count += 1

        return reviews_count

    def _deactivate_demo_listings(self, listings):
        """
        Add a couple of different listing states for demonstration.

        One listing is inactive.
        One listing is soft-deleted.
        """
        if len(listings) < 2:
            return

        inactive_listing = listings[-2]

        inactive_listing.is_active = False
        inactive_listing.save(
            update_fields=[
                "is_active",
            ]
        )

        deleted_listing = listings[-1]

        deleted_listing.is_active = False
        deleted_listing.deleted_at = (
            timezone.now()
            - timedelta(days=30)
        )

        deleted_listing.save(
            update_fields=[
                "is_active",
                "deleted_at",
            ]
        )

    def _make_datetime(
        self,
        days,
        hour,
    ):
        """
        Build timezone-aware booking datetime.

        Check-in is created at 14:00 and check-out at 11:00
        to match the booking rules of the project.
        """
        target_date = (
            timezone.localdate()
            + timedelta(days=days)
        )

        naive_datetime = datetime.combine(
            target_date,
            time(
                hour=hour,
                minute=0,
            ),
        )

        return timezone.make_aware(
            naive_datetime,
            timezone.get_current_timezone(),
        )