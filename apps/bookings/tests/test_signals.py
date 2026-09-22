from datetime import timedelta
from unittest.mock import patch

from django.utils import timezone
from djmoney.money import Money

from apps.bookings.models import Booking
from core.models import BookingStatus


def create_test_booking(
    *,
    tenant,
    listing,
    status=BookingStatus.PENDING,
    snapshot_email=None,
):
    """
    Create a booking with all required snapshot fields.

    This helper is used only in booking signal tests.
    """
    now = timezone.now()

    return Booking.objects.create(
        tenant=tenant,
        listing=listing,
        date_start=now + timedelta(days=10),
        date_end=now + timedelta(days=12),

        snapshot_title="Signal test apartment",
        snapshot_country="DE",
        snapshot_city="Berlin",
        snapshot_district="Mitte",
        snapshot_street="Signal Street",
        snapshot_house_number="10",
        snapshot_apartment_number="5",

        snapshot_first_name=tenant.first_name,
        snapshot_last_name=tenant.last_name,
        snapshot_email=(
            tenant.email
            if snapshot_email is None
            else snapshot_email
        ),
        snapshot_price_per_night=Money(100, "EUR"),

        status=status,
    )


def test_new_booking_sends_notification_to_owner(
    user,
    booking_owner,
    booking_listing,
):
    """
    Check that creating a booking sends an email
    to the listing owner.
    """
    with patch("apps.bookings.signals.send_mail") as mocked_send_mail:
        booking = create_test_booking(
            tenant=user,
            listing=booking_listing,
        )

    mocked_send_mail.assert_called_once()

    call_kwargs = mocked_send_mail.call_args.kwargs

    assert call_kwargs["subject"] == "New booking request"
    assert call_kwargs["recipient_list"] == [booking_owner.email]
    assert booking.snapshot_title in call_kwargs["message"]


def test_new_booking_without_listing_skips_owner_notification(
    user,
):
    """
    Check that no owner email is sent when a new booking
    has no listing.
    """
    with patch("apps.bookings.signals.send_mail") as mocked_send_mail:
        create_test_booking(
            tenant=user,
            listing=None,
        )

    mocked_send_mail.assert_not_called()


def test_new_booking_without_owner_email_skips_notification(
    user,
    booking_owner,
    booking_listing,
):
    """
    Check that no email is sent when the listing owner
    has no email address.
    """
    booking_owner.email = ""
    booking_owner.save(update_fields=["email"])

    with patch("apps.bookings.signals.send_mail") as mocked_send_mail:
        create_test_booking(
            tenant=user,
            listing=booking_listing,
        )

    mocked_send_mail.assert_not_called()


def test_booking_status_change_sends_notification_to_tenant(
    user,
    booking_listing,
):
    """
    Check that changing a booking status sends
    a notification to the tenant.
    """
    with patch("apps.bookings.signals.send_mail") as mocked_send_mail:
        booking = create_test_booking(
            tenant=user,
            listing=booking_listing,
        )

        mocked_send_mail.reset_mock()

        booking.status = BookingStatus.CONFIRMED
        booking.save(update_fields=["status", "updated_at"])

    mocked_send_mail.assert_called_once()

    call_kwargs = mocked_send_mail.call_args.kwargs

    assert call_kwargs["subject"] == (
        f"Booking status changed: {BookingStatus.CONFIRMED}"
    )
    assert call_kwargs["recipient_list"] == [user.email]
    assert "Previous status: pending" in call_kwargs["message"]
    assert "New status: confirmed" in call_kwargs["message"]


def test_booking_status_change_stores_old_status(
    user,
    booking_listing,
):
    """
    Check that the pre_save signal stores
    the previous booking status.
    """
    with patch("apps.bookings.signals.send_mail"):
        booking = create_test_booking(
            tenant=user,
            listing=booking_listing,
        )

        booking.status = BookingStatus.CONFIRMED
        booking.save(update_fields=["status", "updated_at"])

    assert booking._old_status == BookingStatus.PENDING


def test_booking_save_without_status_change_sends_no_email(
    user,
    booking_listing,
):
    """
    Check that saving an existing booking without changing
    its status does not send a notification.
    """
    with patch("apps.bookings.signals.send_mail") as mocked_send_mail:
        booking = create_test_booking(
            tenant=user,
            listing=booking_listing,
        )

        mocked_send_mail.reset_mock()

        booking.snapshot_title = "Updated title"
        booking.save(update_fields=["snapshot_title", "updated_at"])

    mocked_send_mail.assert_not_called()


def test_status_change_without_tenant_email_skips_tenant_notification(
    user,
    booking_listing,
):
    """
    Check that a status-change email is skipped when
    the booking snapshot has no tenant email.
    """
    with patch("apps.bookings.signals.send_mail") as mocked_send_mail:
        booking = create_test_booking(
            tenant=user,
            listing=booking_listing,
            snapshot_email="",
        )

        mocked_send_mail.reset_mock()

        booking.status = BookingStatus.CONFIRMED
        booking.save(update_fields=["status", "updated_at"])

    mocked_send_mail.assert_not_called()


def test_cancelled_booking_notifies_tenant_and_owner(
    user,
    booking_owner,
    booking_listing,
):
    """
    Check that cancellation sends one email to the tenant
    and one email to the listing owner.
    """
    with patch("apps.bookings.signals.send_mail") as mocked_send_mail:
        booking = create_test_booking(
            tenant=user,
            listing=booking_listing,
        )

        mocked_send_mail.reset_mock()

        booking.status = BookingStatus.CANCELLED
        booking.save(update_fields=["status", "updated_at"])

    assert mocked_send_mail.call_count == 2

    first_call = mocked_send_mail.call_args_list[0].kwargs
    second_call = mocked_send_mail.call_args_list[1].kwargs

    assert first_call["recipient_list"] == [user.email]
    assert first_call["subject"] == (
        f"Booking status changed: {BookingStatus.CANCELLED}"
    )

    assert second_call["recipient_list"] == [booking_owner.email]
    assert second_call["subject"] == "Booking cancelled"


def test_cancelled_booking_without_listing_only_notifies_tenant(
    user,
    booking_listing,
):
    """
    Check that cancellation still notifies the tenant
    but skips the owner email when the listing is missing.
    """
    with patch("apps.bookings.signals.send_mail") as mocked_send_mail:
        booking = create_test_booking(
            tenant=user,
            listing=booking_listing,
        )

        mocked_send_mail.reset_mock()

        booking.listing = None
        booking.status = BookingStatus.CANCELLED
        booking.save(
            update_fields=[
                "listing",
                "status",
                "updated_at",
            ]
        )

    mocked_send_mail.assert_called_once()

    call_kwargs = mocked_send_mail.call_args.kwargs

    assert call_kwargs["recipient_list"] == [user.email]


def test_cancelled_booking_without_owner_email_only_notifies_tenant(
    user,
    booking_owner,
    booking_listing,
):
    """
    Check that cancellation skips the owner email
    when the listing owner has no email address.
    """
    with patch("apps.bookings.signals.send_mail") as mocked_send_mail:
        booking = create_test_booking(
            tenant=user,
            listing=booking_listing,
        )

        mocked_send_mail.reset_mock()

        booking_owner.email = ""
        booking_owner.save(update_fields=["email"])

        booking.status = BookingStatus.CANCELLED
        booking.save(update_fields=["status", "updated_at"])

    mocked_send_mail.assert_called_once()

    call_kwargs = mocked_send_mail.call_args.kwargs

    assert call_kwargs["recipient_list"] == [user.email]