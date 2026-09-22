from datetime import timedelta
from io import StringIO

from django.core.management import call_command
from django.utils import timezone

from core.constants import LISTING_SOFT_DELETE_DAYS


def test_delete_old_listings_removes_expired_listing(listing):
    """
    Check that a listing soft-deleted longer than the retention
    period is permanently removed.
    """
    listing.deleted_at = timezone.now() - timedelta(
        days=LISTING_SOFT_DELETE_DAYS + 1
    )
    listing.is_active = False
    listing.save(update_fields=["deleted_at", "is_active"])

    listing_id = listing.id

    call_command("delete_old_listings")

    assert listing.__class__.objects.filter(id=listing_id).exists() is False


def test_delete_old_listings_keeps_recently_deleted_listing(listing):
    """
    Check that a recently soft-deleted listing is not removed.
    """
    listing.deleted_at = timezone.now() - timedelta(
        days=LISTING_SOFT_DELETE_DAYS - 1
    )
    listing.is_active = False
    listing.save(update_fields=["deleted_at", "is_active"])

    listing_id = listing.id

    call_command("delete_old_listings")

    assert listing.__class__.objects.filter(id=listing_id).exists() is True


def test_delete_old_listings_keeps_active_listing(listing):
    """
    Check that an active listing without deleted_at is not removed.
    """
    listing_id = listing.id

    call_command("delete_old_listings")

    assert listing.__class__.objects.filter(id=listing_id).exists() is True


def test_delete_old_listings_writes_success_message(listing):
    """
    Check that the management command writes a success message.
    """
    listing.deleted_at = timezone.now() - timedelta(
        days=LISTING_SOFT_DELETE_DAYS + 1
    )
    listing.is_active = False
    listing.save(update_fields=["deleted_at", "is_active"])

    output = StringIO()

    call_command(
        "delete_old_listings",
        stdout=output,
    )

    assert "Successfully deleted" in output.getvalue()
    assert "expired listings." in output.getvalue()