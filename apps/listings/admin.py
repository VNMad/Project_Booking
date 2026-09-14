from django.contrib import admin
from simple_history.admin import SimpleHistoryAdmin

from .models import Listing, Photo


class PhotoInline(admin.TabularInline):
    model = Photo
    extra = 1
    fields = ("image", "position")


@admin.register(Listing)
class ListingAdmin(SimpleHistoryAdmin):
    list_display = (
        "title",
        "owner",
        "city",
        "country",
        "price_per_night",
        "rooms",
        "is_active",
        "created_at",
    )
    list_filter = ("is_active", "country", "rooms", "created_at")
    search_fields = ("title", "city", "street", "owner__email")
    raw_id_fields = ("owner",)
    inlines = [PhotoInline]


@admin.register(Photo)
class PhotoAdmin(admin.ModelAdmin):
    list_display = ("id", "listing", "position", "created_at")
    list_filter = ("position",)
    raw_id_fields = ("listing",)