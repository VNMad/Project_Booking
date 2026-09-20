from datetime import timedelta

from django.urls import reverse
from django.utils import timezone
from rest_framework import status

from apps.bookings.models import Booking
from apps.users.models import BookingUser
from core.models import BookingStatus


def get_booking_dates(days_start=10, days_end=12):
    """
    Return valid check-in and check-out dates for a test booking.
    """
    now = timezone.now()

    date_start = (
        now + timedelta(days=days_start)
    ).replace(
        hour=14,
        minute=0,
        second=0,
        microsecond=0,
    )

    date_end = (
        now + timedelta(days=days_end)
    ).replace(
        hour=11,
        minute=0,
        second=0,
        microsecond=0,
    )

    return date_start, date_end


def create_booking_for_test(listing, user, days_start=10, days_end=12):
    """
    Create a booking directly through the database for view tests.
    """
    date_start, date_end = get_booking_dates(days_start=days_start, days_end=days_end)

    return Booking.objects.create(
        tenant=user,
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
        snapshot_first_name=user.first_name,
        snapshot_last_name=user.last_name,
        snapshot_email=user.email,
        snapshot_price_per_night=listing.price_per_night,
        status=BookingStatus.PENDING,
    )


def test_list_bookings_requires_authentication(api_client):
    """
    Check that bookings cannot be listed without authentication.
    """
    url = reverse("booking-list")
    response = api_client.get(url)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_list_bookings(api_client, listing, user):
    """
    Check that an authenticated user can list accessible bookings.
    """
    booking = create_booking_for_test(listing=listing, user=user)
    api_client.force_authenticate(user=user)
    url = reverse("booking-list")
    response = api_client.get(url)

    assert response.status_code == status.HTTP_200_OK
    assert response.data["count"] == 1
    assert response.data["results"][0]["id"] == str(booking.id)


def test_create_booking(api_client, listing, user):
    """
    Check that an authenticated user can create a booking.
    """
    api_client.force_authenticate(user=user)
    date_start, date_end = get_booking_dates()
    url = reverse("booking-list")

    data = {
        "listing": str(listing.id),
        "date_start": date_start.isoformat(),
        "date_end": date_end.isoformat(),
    }

    response = api_client.post(url, data, format="json")

    assert response.status_code == status.HTTP_201_CREATED
    booking = Booking.objects.get(id=response.data["id"])

    assert booking.tenant == user
    assert booking.listing == listing
    assert booking.status == BookingStatus.PENDING


def test_create_booking_requires_authentication(api_client, listing):
    """
    Check that an unauthenticated user cannot create a booking.
    """
    date_start, date_end = get_booking_dates()
    url = reverse("booking-list")

    data = {
        "listing": str(listing.id),
        "date_start": date_start.isoformat(),
        "date_end": date_end.isoformat(),
    }

    response = api_client.post(url, data, format="json")

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_create_booking_creates_snapshots(api_client, booking_listing, user):
    """
    Check that booking creation stores property and tenant snapshots.
    """
    api_client.force_authenticate(user=user)
    date_start, date_end = get_booking_dates()
    url = reverse("booking-list")

    data = {
        "listing": str(booking_listing.id),
        "date_start": date_start.isoformat(),
        "date_end": date_end.isoformat(),
    }

    response = api_client.post(url, data, format="json")

    assert response.status_code == status.HTTP_201_CREATED

    booking = Booking.objects.get(id=response.data["id"])

    assert booking.snapshot_title == booking_listing.title
    assert booking.snapshot_country == booking_listing.country
    assert booking.snapshot_city == booking_listing.city
    assert booking.snapshot_district == booking_listing.district
    assert booking.snapshot_street == booking_listing.street
    assert booking.snapshot_house_number == booking_listing.house_number
    assert booking.snapshot_apartment_number == booking_listing.apartment_number

    assert booking.snapshot_first_name == user.first_name
    assert booking.snapshot_last_name == user.last_name
    assert booking.snapshot_email == user.email

    assert booking.snapshot_price_per_night == booking_listing.price_per_night


def test_retrieve_booking(api_client, listing, user):
    """
    Check that a tenant can retrieve their booking.
    """
    booking = create_booking_for_test(listing=listing, user=user)
    api_client.force_authenticate(user=user)
    url = reverse("booking-detail", kwargs={"pk": booking.id})
    response = api_client.get(url)

    assert response.status_code == status.HTTP_200_OK
    assert response.data["id"] == str(booking.id)
    assert response.data["listing"] == listing.id
    assert response.data["status"] == BookingStatus.PENDING


def test_listing_owner_can_retrieve_booking(api_client, listing, user):
    """
    Check that the listing owner can retrieve a booking.
    """
    tenant = BookingUser.objects.create_user(
        email="bookingtenant@example.com",
        password="TestPassword1!",
        first_name="Booking",
        last_name="Tenant",
        phone="+491111111111",
    )

    booking = create_booking_for_test(listing=listing, user=tenant)
    api_client.force_authenticate(user=listing.owner)
    url = reverse("booking-detail", kwargs={"pk": booking.id})
    response = api_client.get(url)

    assert response.status_code == status.HTTP_200_OK
    assert response.data["id"] == str(booking.id)


def test_other_user_cannot_retrieve_booking(api_client, listing, user):
    """
    Check that an unrelated user cannot retrieve a booking.
    """
    booking = create_booking_for_test(listing=listing, user=user)

    other_user = BookingUser.objects.create_user(
        email="unrelated@example.com",
        password="TestPassword1!",
        first_name="Unrelated",
        last_name="User",
        phone="+492222222222",
    )

    api_client.force_authenticate(user=other_user)
    url = reverse("booking-detail", kwargs={"pk": booking.id})
    response = api_client.get(url)

    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_booking_cannot_be_updated(api_client, listing, user):
    """
    Check that a booking cannot be fully updated.
    """
    booking = create_booking_for_test(listing=listing, user=user)
    api_client.force_authenticate(user=user)
    url = reverse("booking-detail", kwargs={"pk": booking.id})
    response = api_client.put(url, {"status": BookingStatus.CONFIRMED}, format="json")

    assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED


def test_booking_cannot_be_partially_updated(api_client, listing, user):
    """
    Check that a booking cannot be partially updated.
    """
    booking = create_booking_for_test(listing=listing, user=user)
    api_client.force_authenticate(user=user)
    url = reverse("booking-detail", kwargs={"pk": booking.id})
    response = api_client.patch(url, {"date_end": "2026-12-01T11:00:00Z"}, format="json")

    assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED


def test_booking_cannot_be_deleted(api_client, listing, user):
    """
    Check that a booking cannot be deleted.
    """
    booking = create_booking_for_test(listing=listing, user=user)
    api_client.force_authenticate(user=user)
    url = reverse("booking-detail", kwargs={"pk": booking.id})
    response = api_client.delete(url)

    assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED

    booking.refresh_from_db()
    assert Booking.objects.filter(id=booking.id).exists()


def test_confirm_booking(api_client, listing, user):
    """
    Check that the listing owner can confirm a pending booking.
    """
    tenant = BookingUser.objects.create_user(
        email="confirmtenant@example.com",
        password="TestPassword1!",
        first_name="Confirm",
        last_name="Tenant",
        phone="+493333333333",
    )

    booking = create_booking_for_test(listing=listing, user=tenant)
    api_client.force_authenticate(user=listing.owner)
    url = reverse("booking-confirm", kwargs={"pk": booking.id})

    response = api_client.post(url)

    assert response.status_code == status.HTTP_200_OK
    assert response.data["status"] == BookingStatus.CONFIRMED

    booking.refresh_from_db()

    assert booking.status == BookingStatus.CONFIRMED


def test_confirm_booking_forbidden_for_tenant(api_client, booking_listing, user):
    """
    Check that the tenant cannot confirm their own booking.
    """
    booking = create_booking_for_test(listing=booking_listing, user=user)
    api_client.force_authenticate(user=user)
    url = reverse("booking-confirm", kwargs={"pk": booking.id})
    response = api_client.post(url)

    assert response.status_code == status.HTTP_400_BAD_REQUEST

    booking.refresh_from_db()

    assert booking.status == BookingStatus.PENDING


def test_reject_booking(
    api_client,
    listing,
    user,
):
    """
    Check that the listing owner can reject a pending booking.
    """
    tenant = BookingUser.objects.create_user(
        email="rejecttenant@example.com",
        password="TestPassword1!",
        first_name="Reject",
        last_name="Tenant",
        phone="+494444444444",
    )

    booking = create_booking_for_test(
        listing=listing,
        user=tenant,
    )

    api_client.force_authenticate(user=listing.owner)

    url = reverse(
        "booking-reject",
        kwargs={"pk": booking.id},
    )

    response = api_client.post(url)

    assert response.status_code == status.HTTP_200_OK

    booking.refresh_from_db()

    assert booking.status == BookingStatus.REJECTED


def test_reject_booking_forbidden_for_tenant(
    api_client,
    booking_listing,
    user,
):
    """
    Check that the tenant cannot reject their own booking.
    """
    booking = create_booking_for_test(
        listing=booking_listing,
        user=user,
    )

    api_client.force_authenticate(user=user)

    url = reverse(
        "booking-reject",
        kwargs={"pk": booking.id},
    )

    response = api_client.post(url)

    assert response.status_code == status.HTTP_400_BAD_REQUEST

    booking.refresh_from_db()

    assert booking.status == BookingStatus.PENDING

def test_cancel_booking(
    api_client,
    listing,
    user,
):
    """
    Check that the tenant can cancel a pending booking
    before the cancellation deadline.
    """
    booking = create_booking_for_test(
        listing=listing,
        user=user,
        days_start=10,
        days_end=12,
    )

    api_client.force_authenticate(user=user)

    url = reverse(
        "booking-cancel",
        kwargs={"pk": booking.id},
    )

    response = api_client.post(url)

    assert response.status_code == status.HTTP_200_OK
    assert response.data["status"] == BookingStatus.CANCELLED

    booking.refresh_from_db()

    assert booking.status == BookingStatus.CANCELLED


def test_cancel_booking_forbidden_for_listing_owner(
    api_client,
    listing,
    user,
):
    """
    Check that the listing owner cannot cancel the tenant's booking.
    """
    tenant = BookingUser.objects.create_user(
        email="canceltenant@example.com",
        password="TestPassword1!",
        first_name="Cancel",
        last_name="Tenant",
        phone="+495555555555",
    )

    booking = create_booking_for_test(
        listing=listing,
        user=tenant,
    )

    api_client.force_authenticate(user=listing.owner)

    url = reverse(
        "booking-cancel",
        kwargs={"pk": booking.id},
    )

    response = api_client.post(url)

    assert response.status_code == status.HTTP_400_BAD_REQUEST

    booking.refresh_from_db()

    assert booking.status == BookingStatus.PENDING


def test_create_booking(api_client, booking_listing, user):
    """
    Check that an authenticated user can create a booking.
    """
    api_client.force_authenticate(user=user)

    date_start, date_end = get_booking_dates()

    url = reverse("booking-list")

    data = {
        "listing": str(booking_listing.id),
        "date_start": date_start.isoformat(),
        "date_end": date_end.isoformat(),
    }

    response = api_client.post(
        url,
        data,
        format="json",
    )

    assert response.status_code == status.HTTP_201_CREATED

    booking = Booking.objects.get(
        id=response.data["id"],
    )

    assert booking.tenant == user
    assert booking.listing == booking_listing
    assert booking.status == BookingStatus.PENDING


def test_create_booking_for_inactive_listing(
    api_client,
    listing,
    user,
):
    """
    Check that an inactive listing cannot be booked.
    """
    listing.is_active = False
    listing.save(update_fields=["is_active"])

    api_client.force_authenticate(user=user)

    date_start, date_end = get_booking_dates()

    url = reverse("booking-list")

    data = {
        "listing": str(listing.id),
        "date_start": date_start.isoformat(),
        "date_end": date_end.isoformat(),
    }

    response = api_client.post(
        url,
        data,
        format="json",
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_create_booking_for_deleted_listing(
    api_client,
    listing,
    user,
):
    """
    Check that a soft-deleted listing cannot be booked.
    """
    listing.deleted_at = timezone.now()
    listing.is_active = False
    listing.save(update_fields=["deleted_at", "is_active"])

    api_client.force_authenticate(user=user)

    date_start, date_end = get_booking_dates()

    url = reverse("booking-list")

    data = {
        "listing": str(listing.id),
        "date_start": date_start.isoformat(),
        "date_end": date_end.isoformat(),
    }

    response = api_client.post(
        url,
        data,
        format="json",
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_create_overlapping_booking_is_rejected(
    api_client,
    listing,
    user,
):
    """
    Check that overlapping pending bookings are rejected.
    """
    tenant_one = BookingUser.objects.create_user(
        email="tenantone@example.com",
        password="TestPassword1!",
        first_name="Tenant",
        last_name="One",
        phone="+496666666666",
    )

    create_booking_for_test(
        listing=listing,
        user=tenant_one,
        days_start=10,
        days_end=15,
    )

    api_client.force_authenticate(user=user)

    date_start, date_end = get_booking_dates(
        days_start=12,
        days_end=17,
    )

    url = reverse("booking-list")

    data = {
        "listing": str(listing.id),
        "date_start": date_start.isoformat(),
        "date_end": date_end.isoformat(),
    }

    response = api_client.post(
        url,
        data,
        format="json",
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_adjacent_bookings_are_allowed(
    api_client,
    booking_listing,
    user,
):
    """
    Check that a booking can start exactly when another booking ends.
    """
    tenant_one = BookingUser.objects.create_user(
        email="adjacentone@example.com",
        password="TestPassword1!",
        first_name="Adjacent",
        last_name="One",
        phone="+497777777777",
    )

    create_booking_for_test(
        listing=booking_listing,
        user=tenant_one,
        days_start=10,
        days_end=15,
    )

    api_client.force_authenticate(user=user)

    date_start, date_end = get_booking_dates(
        days_start=15,
        days_end=20,
    )

    url = reverse("booking-list")

    data = {
        "listing": str(booking_listing.id),
        "date_start": date_start.isoformat(),
        "date_end": date_end.isoformat(),
    }

    response = api_client.post(
        url,
        data,
        format="json",
    )

    assert response.status_code == status.HTTP_201_CREATED


def test_retrieve_finished_confirmed_booking_marks_it_completed(
    api_client,
    listing,
    user,
):
    """
    Check that a confirmed booking becomes completed
    after its check-out time has passed.
    """
    date_start = timezone.now() - timedelta(days=5)
    date_end = timezone.now() - timedelta(days=2)

    booking = Booking.objects.create(
        tenant=user,
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
        snapshot_first_name=user.first_name,
        snapshot_last_name=user.last_name,
        snapshot_email=user.email,
        snapshot_price_per_night=listing.price_per_night,
        status=BookingStatus.CONFIRMED,
    )

    api_client.force_authenticate(user=user)

    url = reverse(
        "booking-detail",
        kwargs={"pk": booking.id},
    )

    response = api_client.get(url)

    assert response.status_code == status.HTTP_200_OK
    assert response.data["status"] == BookingStatus.COMPLETED

    booking.refresh_from_db()

    assert booking.status == BookingStatus.COMPLETED