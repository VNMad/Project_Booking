import logging

from django.conf import settings
from django.core.mail import send_mail
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver

from apps.bookings.models import Booking
from core.models import BookingStatus


logger = logging.getLogger(__name__)


@receiver(pre_save, sender=Booking, dispatch_uid="booking_status_change_check")
def booking_status_change_check(sender, instance, **kwargs):
    """
    Store the previous booking status before saving an existing booking.
    The previous status is later used by the post_save signal to determine
    whether the booking status has actually changed.
    """
    if not instance.pk:
        instance._old_status = None
        return

    try:
        old_booking = Booking.objects.get(pk=instance.pk)
        instance._old_status = old_booking.status
    except Booking.DoesNotExist:
        instance._old_status = None


@receiver(post_save, sender=Booking, dispatch_uid="booking_notification")
def booking_notification(sender, instance, created, **kwargs):
    """
    Send email notifications when a booking is created or its status changes.
    A new booking sends a notification to the listing owner.
    When an existing booking changes its status, the tenant is notified.
    When a booking is cancelled, the listing owner is also notified.
    """
    old_status = getattr(instance, "_old_status", None)

    # ---------------------------------------------------------
    # 1. New booking
    # ---------------------------------------------------------
    if created:
        if instance.listing_id is None:
            logger.warning("Booking %s has no listing. Owner notification was skipped.",instance.id)
            return

        owner = instance.listing.owner

        if owner is None or not owner.email:
            logger.warning("Booking %s has no listing owner email. Owner notification was skipped.",instance.id)
            return

        send_mail(
            subject="New booking request",
            message=(
                "A new booking request has been created for your listing.\n\n"
                f"Property: {instance.snapshot_title}\n"
                f"Tenant: {instance.snapshot_first_name} "
                f"{instance.snapshot_last_name}\n"
                f"Tenant email: {instance.snapshot_email}\n"
                f"Check-in: {instance.date_start}\n"
                f"Check-out: {instance.date_end}\n"
                f"Status: {instance.status}"
            ),
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[owner.email],
            fail_silently=False,
        )

        logger.info("New booking notification sent for booking %s to owner %s.",instance.id, owner.email)
        return

    # ---------------------------------------------------------
    # 2. Existing booking: status did not change
    # ---------------------------------------------------------
    if old_status == instance.status:
        return

    # ---------------------------------------------------------
    # 3. Existing booking: notify tenant
    # ---------------------------------------------------------
    if instance.snapshot_email:
        send_mail(
            subject=f"Booking status changed: {instance.status}",
            message=(
                "Your booking status has changed.\n\n"
                f"Property: {instance.snapshot_title}\n"
                f"Previous status: {old_status}\n"
                f"New status: {instance.status}\n"
                f"Check-in: {instance.date_start}\n"
                f"Check-out: {instance.date_end}"
            ),
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[instance.snapshot_email],
            fail_silently=False,
        )

        logger.info("Booking status notification sent for booking %s to tenant %s.",
                    instance.id, instance.snapshot_email)
    else:
        logger.warning("Booking %s has no tenant email. Tenant notification was skipped.",instance.id)

    # ---------------------------------------------------------
    # 4. Booking cancelled: notify listing owner
    # ---------------------------------------------------------
    if instance.status == BookingStatus.CANCELLED:
        if instance.listing_id is None:
            logger.warning("Booking %s has no listing. Owner notification was skipped.",instance.id)
            return

        owner = instance.listing.owner

        if owner is None or not owner.email:
            logger.warning("Booking %s has no listing owner email. Owner notification was skipped.",
                           instance.id)
            return

        send_mail(
            subject="Booking cancelled",
            message=(
                "A booking for your listing has been cancelled by the tenant.\n\n"
                f"Property: {instance.snapshot_title}\n"
                f"Tenant: {instance.snapshot_first_name} "
                f"{instance.snapshot_last_name}\n"
                f"Tenant email: {instance.snapshot_email}\n"
                f"Check-in: {instance.date_start}\n"
                f"Check-out: {instance.date_end}"
            ),
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[owner.email],
            fail_silently=False,
        )

        logger.info("Booking cancellation notification sent for booking %s to owner %s.",
                    instance.id, owner.email)