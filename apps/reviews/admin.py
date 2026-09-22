from django.contrib import admin
from simple_history.admin import SimpleHistoryAdmin

from .models import Review


@admin.register(Review)
class ReviewAdmin(SimpleHistoryAdmin):
    list_display = (
        "id",
        "booking",
        "cleanliness_rating",
        "location_rating",
        "created_at",
    )
    list_select_related = ("booking",)
    list_filter = ("cleanliness_rating", "location_rating", "created_at")
    search_fields = ("booking__snapshot_title", "comment")
    raw_id_fields = ("booking",)