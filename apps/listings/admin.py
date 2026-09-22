from simple_history.admin import SimpleHistoryAdmin
from django.contrib import admin
from django.db.models import Avg, Count
from django.urls import reverse
from django.utils.html import format_html_join

from apps.reviews.models import Review
from .models import Listing, Photo
from core.constants import LISTING_MAX_PHOTOS


class PhotoInline(admin.TabularInline):
    model = Photo
    extra = 1
    max_num = LISTING_MAX_PHOTOS
    validate_max = True
    fields = ("image", "position")


@admin.register(Listing)
class ListingAdmin(SimpleHistoryAdmin):

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.annotate(admin_reviews_count=Count("bookings__review", distinct=True),
                                 admin_average_cleanliness=Avg("bookings__review__cleanliness_rating"),
                                 admin_average_location=Avg("bookings__review__location_rating"))

    @admin.display(description="Reviews", ordering="admin_reviews_count")
    def reviews_count(self, obj):
        return obj.admin_reviews_count

    @admin.display(description="Cleanliness", ordering="admin_average_cleanliness")
    def average_cleanliness(self, obj):
        if obj.admin_average_cleanliness is None:
            return "-"
        return round(obj.admin_average_cleanliness, 2)

    @admin.display(description="Location", ordering="admin_average_location")
    def average_location(self, obj):
        if obj.admin_average_location is None:
            return "-"
        return round(obj.admin_average_location, 2)

    @admin.display(description="Reviews")
    def reviews_details(self, obj):
        """
        Display all reviews associated with this listing
        through its bookings.
        """
        reviews = (Review.objects.filter(booking__listing=obj).select_related("booking", "booking__tenant")
                         .order_by("-created_at"))
        if not reviews.exists():
            return "No reviews yet."
        return format_html_join(
            "",
            (
                '<div style="margin-bottom: 15px; '
                'padding: 10px; '
                'border: 1px solid #ddd; '
                'border-radius: 5px;">'
                '<strong>Cleanliness:</strong> {}/5<br>'
                '<strong>Location:</strong> {}/5<br>'
                '<strong>Comment:</strong> {}<br>'
                '<strong>Tenant:</strong> {}<br>'
                '<a href="{}">Open review</a>'
                "</div>"
            ),
            (
                (
                    review.cleanliness_rating,
                    review.location_rating,
                    review.comment or "-",
                    review.booking.snapshot_email,
                    reverse(
                        "admin:reviews_review_change",
                        args=[review.pk],
                    ),
                )
                for review in reviews
            ),
        )
    readonly_fields = ("reviews_details",)
    list_display = (
        "title",
        "owner",
        "city",
        "country",
        "price_per_night",
        "rooms",
        "reviews_count",
        "average_cleanliness",
        "average_location",
        "is_active",
        "created_at",
    )
    list_select_related = ("owner",)
    list_filter = ("is_active", "country", "rooms", "created_at")
    search_fields = ("title", "city", "street", "owner__email")
    raw_id_fields = ("owner",)
    inlines = [PhotoInline]


@admin.register(Photo)
class PhotoAdmin(admin.ModelAdmin):
    list_display = ("id", "listing", "position", "created_at")
    list_filter = ("position",)
    raw_id_fields = ("listing",)