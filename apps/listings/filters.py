from django_filters import rest_framework as filters

from .models import Listing


class ListingFilter(filters.FilterSet):
    price_min = filters.NumberFilter(field_name="price_per_night", lookup_expr="gte")
    price_max = filters.NumberFilter(field_name="price_per_night", lookup_expr="lte")

    class Meta:
        model = Listing
        fields = [
            "country",
            "city",
            "district",
            "rooms",
            "price_min",
            "price_max",
        ]