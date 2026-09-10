from datetime import timedelta
from django.core.management.base import BaseCommand
from django.utils import timezone
from apps.listings.models import Listing


class Command(BaseCommand):
    help = "Permanently deletes listings soft-deleted more than 180 days ago."

    def handle(self, *args, **options):
        limit_date = timezone.now() - timedelta(days=180)

        old_listings = Listing.objects.filter(deleted_at__lt=limit_date)
        count, _ = old_listings.delete()

        self.stdout.write(self.style.SUCCESS(f"Successfully deleted {count} expired listings."))