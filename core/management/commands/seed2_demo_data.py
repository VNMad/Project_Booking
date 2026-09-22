from datetime import datetime, time, timedelta

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from djmoney.money import Money
from simple_history.utils import bulk_create_with_history

from apps.bookings.models import Booking
from apps.listings.models import Listing
from apps.reviews.models import Review
from core.models import BookingStatus


DEMO_SUFFIX = " [DEMO]"


DEMO_USERS = (
    {
        "email": "owner1@admin.com",
        "first_name": "Owner",
        "last_name": "One",
        "phone": "+491111111111",
        "is_staff": True,
        "is_superuser": True,
    },
    {
        "email": "owner2@admin.com",
        "first_name": "Owner",
        "last_name": "Two",
        "phone": "+491111111112",
        "is_staff": False,
        "is_superuser": False,
    },
    {
        "email": "tenant1@admin.com",
        "first_name": "Tenant",
        "last_name": "One",
        "phone": "+492222222221",
        "is_staff": False,
        "is_superuser": False,
    },
    {
        "email": "tenant2@admin.com",
        "first_name": "Tenant",
        "last_name": "Two",
        "phone": "+492222222222",
        "is_staff": False,
        "is_superuser": False,
    },
    {
        "email": "tenant3@admin.com",
        "first_name": "Tenant",
        "last_name": "Three",
        "phone": "+492222222223",
        "is_staff": False,
        "is_superuser": False,
    },
    {
        "email": "tenant4@admin.com",
        "first_name": "Tenant",
        "last_name": "Four",
        "phone": "+492222222224",
        "is_staff": False,
        "is_superuser": False,
    },
    {
        "email": "tenant5@admin.com",
        "first_name": "Tenant",
        "last_name": "Five",
        "phone": "+492222222225",
        "is_staff": False,
        "is_superuser": False,
    },
)


LISTING_DATA = (
    {
        "owner_email": "owner1@admin.com",
        "title": "Berlin Mitte Apartment",
        "description": (
            "Modern apartment in Berlin Mitte, close to public transport "
            "and the city centre."
        ),
        "country": "DE",
        "city": "Berlin",
        "district": "Mitte",
        "street": "Friedrichstrasse",
        "house_number": "101",
        "apartment_number": "12",
        "price": 120,
        "rooms": "2",
    },
    {
        "owner_email": "owner1@admin.com",
        "title": "Hamburg Altona Apartment",
        "description": (
            "Comfortable apartment in Hamburg Altona with convenient "
            "connections to the city centre."
        ),
        "country": "DE",
        "city": "Hamburg",
        "district": "Altona",
        "street": "Ottenser Hauptstrasse",
        "house_number": "22",
        "apartment_number": "7",
        "price": 105,
        "rooms": "2",
    },
    {
        "owner_email": "owner2@admin.com",
        "title": "Munich Schwabing Apartment",
        "description": (
            "Spacious apartment in Munich Schwabing near cafes, parks "
            "and public transport."
        ),
        "country": "DE",
        "city": "Munich",
        "district": "Schwabing",
        "street": "Leopoldstrasse",
        "house_number": "88",
        "apartment_number": "15",
        "price": 145,
        "rooms": "3",
    },
    {
        "owner_email": "owner2@admin.com",
        "title": "Cologne City Apartment",
        "description": (
            "Bright apartment in central Cologne with easy access to "
            "the old town and main station."
        ),
        "country": "DE",
        "city": "Cologne",
        "district": "Innenstadt",
        "street": "Hohe Strasse",
        "house_number": "64",
        "apartment_number": "9",
        "price": 115,
        "rooms": "2",
    },
)


BOOKING_PATTERNS = (
    {
        "status": BookingStatus.COMPLETED,
        "start_days": -90,
        "end_days": -87,
    },
    {
        "status": BookingStatus.COMPLETED,
        "start_days": -60,
        "end_days": -57,
    },
    {
        "status": BookingStatus.COMPLETED,
        "start_days": -30,
        "end_days": -27,
    },
    {
        "status": BookingStatus.CONFIRMED,
        "start_days": 7,
        "end_days": 10,
    },
    {
        "status": BookingStatus.REJECTED,
        "start_days": 14,
        "end_days": 17,
    },
    {
        "status": BookingStatus.CANCELLED,
        "start_days": 21,
        "end_days": 24,
    },
)


REVIEW_DATA = (
    {
        "cleanliness_rating": 5,
        "location_rating": 5,
        "comment": "Excellent apartment, very clean and well located.",
    },
    {
        "cleanliness_rating": 4,
        "location_rating": 5,
        "comment": "Very good stay with a convenient location.",
    },
    {
        "cleanliness_rating": 5,
        "location_rating": 4,
        "comment": "Clean, comfortable and easy to reach.",
    },
)


class Command(BaseCommand):
    """
    Create a small deterministic demo dataset for presentations.

    The command does not use Faker. It always creates the same:
    - 2 owners
    - 5 tenants
    - 4 listings
    - 24 bookings
    - 12 reviews
    """

    help = (
        "Creates a deterministic demo dataset with 2 owners, "
        "5 tenants, 4 listings, 24 bookings and 12 reviews."
    )

    @transaction.atomic
    def handle(self, *args, **options):
        password = settings.DEMO_USER_PASSWORD

        self.stdout.write(
            f"Removing previously generated seed2 data{DEMO_SUFFIX}..."
        )
        self._clear_demo_data()

        self.stdout.write(
            f"Creating demo users{DEMO_SUFFIX}..."
        )
        users = self._create_users(password)

        self.stdout.write(
            f"Creating 4 listings{DEMO_SUFFIX}..."
        )
        listings = self._create_listings(users)

        self.stdout.write(
            f"Creating 24 bookings{DEMO_SUFFIX}..."
        )
        bookings = self._create_bookings(
            listings=listings,
            users=users,
        )

        self.stdout.write(
            f"Creating reviews for completed bookings{DEMO_SUFFIX}..."
        )
        reviews_count = self._create_reviews(bookings)

        self.stdout.write("")
        self.stdout.write(
            self.style.SUCCESS(
                f"Seed2 demo data created successfully{DEMO_SUFFIX}."
            )
        )
        self.stdout.write(f"Users: {len(users)}")
        self.stdout.write("Owners: 2")
        self.stdout.write("Tenants: 5")
        self.stdout.write(f"Listings: {len(listings)}")
        self.stdout.write(f"Bookings: {len(bookings)}")
        self.stdout.write(f"Reviews: {reviews_count}")

        self.stdout.write("")
        self.stdout.write("Demo users:")

        for email in users:
            self.stdout.write(f"  - {email}")

        self.stdout.write("")
        self.stdout.write(
            "Password is taken from DEMO_USER_PASSWORD."
        )

    def _clear_demo_data(self):
        """
        Remove only data created by seed2_demo_data.

        The original seed_demo_data command uses titles beginning
        with "[DEMO]". This command uses titles ending with "[DEMO]",
        so the two demo datasets can be distinguished.
        """
        demo_bookings = Booking.objects.filter(
            snapshot_title__endswith=DEMO_SUFFIX,
        )

        Review.objects.filter(
            booking__in=demo_bookings,
        ).delete()

        demo_bookings.delete()

        Listing.objects.filter(
            title__endswith=DEMO_SUFFIX,
        ).delete()

    def _create_users(self, password):
        """Create or update two owners and five tenants."""
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

    def _create_listings(self, users):
        """
        Create four fixed German apartment listings.

        Two listings belong to owner1 and two listings belong to owner2.
        Listing titles and descriptions end with "[DEMO]".
        """
        listings = []

        for listing_data in LISTING_DATA:
            listing = Listing.objects.create(
                owner=users[listing_data["owner_email"]],
                title=f"{listing_data['title']}{DEMO_SUFFIX}",
                description=f"{listing_data['description']}{DEMO_SUFFIX}",
                country=listing_data["country"],
                city=listing_data["city"],
                district=listing_data["district"],
                street=listing_data["street"],
                house_number=listing_data["house_number"],
                apartment_number=listing_data["apartment_number"],
                price_per_night=Money(
                    listing_data["price"],
                    "EUR",
                ),
                rooms=listing_data["rooms"],
                is_active=True,
            )

            listings.append(listing)

        return listings

    def _create_bookings(self, listings, users):
        """
        Create exactly six bookings for each listing:

        - 3 COMPLETED
        - 1 CONFIRMED
        - 1 REJECTED
        - 1 CANCELLED

        Total: 4 listings x 6 bookings = 24 bookings.

        Five tenants are rotated through the 24 bookings. Because
        24 cannot be divided equally by 5, the final distribution is:
        5, 5, 5, 5 and 4 bookings.
        """
        tenants = (
            users["tenant1@admin.com"],
            users["tenant2@admin.com"],
            users["tenant3@admin.com"],
            users["tenant4@admin.com"],
            users["tenant5@admin.com"],
        )

        bookings = []
        booking_index = 0

        for listing in listings:
            for pattern in BOOKING_PATTERNS:
                tenant = tenants[
                    booking_index % len(tenants)
                ]

                booking = Booking(
                    tenant=tenant,
                    listing=listing,
                    date_start=self._make_datetime(
                        days=pattern["start_days"],
                        hour=14,
                    ),
                    date_end=self._make_datetime(
                        days=pattern["end_days"],
                        hour=11,
                    ),
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
                    status=pattern["status"],
                )

                bookings.append(booking)
                booking_index += 1

        # Booking post_save signals send notification emails.
        # bulk_create_with_history creates records and history
        # without triggering normal save signals.
        bulk_create_with_history(
            bookings,
            Booking,
            batch_size=100,
        )

        return bookings

    def _create_reviews(self, bookings):
        """
        Create one review for every COMPLETED booking.

        Every listing has three COMPLETED bookings, therefore:
        4 listings x 3 completed bookings = 12 reviews.
        """
        reviews_count = 0
        completed_index = 0

        for booking in bookings:
            if booking.status != BookingStatus.COMPLETED:
                continue

            review_data = REVIEW_DATA[
                completed_index % len(REVIEW_DATA)
            ]

            Review.objects.create(
                booking=booking,
                cleanliness_rating=review_data["cleanliness_rating"],
                location_rating=review_data["location_rating"],
                comment=f"{review_data['comment']}{DEMO_SUFFIX}",
            )

            reviews_count += 1
            completed_index += 1

        return reviews_count

    def _make_datetime(
        self,
        days,
        hour,
    ):
        """
        Build a timezone-aware booking datetime.

        Check-in is 14:00 and check-out is 11:00,
        matching the booking rules of the project.
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