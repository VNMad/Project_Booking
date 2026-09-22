from django.contrib import admin
from simple_history.admin import SimpleHistoryAdmin

from apps.reviews.models import Review
from .models import Booking


class ReviewInline(admin.StackedInline):
    model = Review
    can_delete = False
    extra = 0
    readonly_fields = ("cleanliness_rating", "location_rating", "comment")


class BookingRelationFilter(admin.SimpleListFilter):
    """
    Filter bookings by the relation of the logged-in user
    to the booking.
    """

    title = "Booking relation"
    parameter_name = "relation"

    def lookups(self, request, model_admin):
        return ("my", "My bookings"), ("my_listings", "Bookings for my listings")

    def queryset(self, request, queryset):
        if self.value() == "my":
            return queryset.filter(tenant=request.user)
        if self.value() == "my_listings":
            return queryset.filter(listing__owner=request.user)
        return queryset


@admin.register(Booking)
class BookingAdmin(SimpleHistoryAdmin):
    list_display = (
        "id",
        "snapshot_title",
        "tenant",
        "status",
        "date_start",
        "date_end",
        "snapshot_price_per_night",
    )
    list_select_related = ("tenant", "listing", "listing__owner")
    list_filter = (BookingRelationFilter, "status", "date_start", "date_end", "snapshot_country")
    search_fields = (
        "snapshot_title",
        "snapshot_email",
        "snapshot_first_name",
        "snapshot_last_name",
        "tenant__email",
    )
    raw_id_fields = ("tenant", "listing")
    inlines = [ReviewInline]

    fieldsets = (
        (None, {"fields": ("tenant", "listing", "status", "date_start", "date_end")}),
        (
            "Property Snapshot",
            {
                "fields": (
                    "snapshot_title",
                    "snapshot_country",
                    "snapshot_city",
                    "snapshot_district",
                    "snapshot_street",
                    "snapshot_house_number",
                    "snapshot_apartment_number",
                    "snapshot_price_per_night",
                )
            },
        ),
        (
            "Tenant Snapshot",
            {
                "fields": (
                    "snapshot_first_name",
                    "snapshot_last_name",
                    "snapshot_email",
                )
            },
        ),
    )