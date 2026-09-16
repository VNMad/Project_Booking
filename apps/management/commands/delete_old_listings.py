import logging
from datetime import timedelta
from django.core.management.base import BaseCommand
from django.utils import timezone
from apps.listings.models import Listing
from core.constants import LISTING_SOFT_DELETE_DAYS


logger = logging.getLogger(__name__)

class Command(BaseCommand):
    """
    Permanently delete listings that have been soft-deleted
    for longer than the configured retention period.
    """

    help = f"Permanently deletes listings soft-deleted more than {LISTING_SOFT_DELETE_DAYS} days ago."

    def handle(self, *args, **options):
        """
        Find expired soft-deleted listings and permanently delete them.

        The retention period is defined by LISTING_SOFT_DELETE_DAYS.
        """
        limit_date = timezone.now() - timedelta(days=LISTING_SOFT_DELETE_DAYS)

        old_listings = Listing.objects.filter(deleted_at__lt=limit_date)
        count, _ = old_listings.delete()

        logger.info("Successfully deleted %s expired listings.", count)
        self.stdout.write(self.style.SUCCESS(f"Successfully deleted {count} expired listings."))