from django.db.models import Avg, Count, Q
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import status, viewsets
from rest_framework.exceptions import NotFound, PermissionDenied
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.decorators import action

from apps.bookings.models import Booking
from apps.listings.models import Listing
from apps.reviews.models import Review
from core.models import BookingStatus

from .serializers import ListingRatingSerializer, ListingStatisticsSerializer


@extend_schema_view(
    retrieve=extend_schema(summary="Get public listing rating",
        description=("Return public rating statistics for an active rental listing."),
        responses=ListingRatingSerializer))
class ListingStatisticsViewSet(viewsets.ViewSet):

    def get_permissions(self):
        if self.action == "owner_statistics":
            return [IsAuthenticated()]

        return [AllowAny()]

    def retrieve(self, request, pk=None):
        try:
            listing = Listing.objects.get(pk=pk, is_active=True, deleted_at__isnull=True)
        except Listing.DoesNotExist:
            raise NotFound("Listing not found.")

        statistics = Review.objects.filter(booking__listing=listing).aggregate(
            reviews_count=Count("id"),
            average_cleanliness=Avg("cleanliness_rating"),
            average_location=Avg("location_rating"),
        )

        data = {
            "listing_id": listing.id,
            "reviews_count": statistics["reviews_count"],
            "average_cleanliness": statistics["average_cleanliness"],
            "average_location": statistics["average_location"],
        }

        serializer = ListingRatingSerializer(data)

        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        summary="Get private listing statistics",
        description=("Return detailed statistics for a rental listing. "
                    "Only the listing owner can access this endpoint."),
        responses=ListingStatisticsSerializer)
    @action(detail=True, methods=["get"], url_path="owner")
    def owner_statistics(self, request, pk=None):
        try:
            listing = Listing.objects.get(pk=pk)
        except Listing.DoesNotExist:
            raise NotFound("Listing not found.")

        if listing.owner_id != request.user.id:
            raise PermissionDenied("Only the listing owner can view private statistics.")

        review_statistics = Review.objects.filter(booking__listing=listing).aggregate(
            reviews_count=Count("id"),
            average_cleanliness=Avg("cleanliness_rating"),
            average_location=Avg("location_rating"))

        booking_statistics = Booking.objects.filter(listing=listing).aggregate(
            bookings_count=Count("id"),
            confirmed_bookings=Count("id", filter=Q(status=BookingStatus.CONFIRMED)),
            completed_bookings=Count("id", filter=Q(status=BookingStatus.COMPLETED)),
        )

        data = {
            "listing_id": listing.id,
            "reviews_count": review_statistics["reviews_count"],
            "average_cleanliness": review_statistics["average_cleanliness"],
            "average_location": review_statistics["average_location"],
            "bookings_count": booking_statistics["bookings_count"],
            "confirmed_bookings": booking_statistics["confirmed_bookings"],
            "completed_bookings": booking_statistics["completed_bookings"],
        }

        serializer = ListingStatisticsSerializer(data)

        return Response(serializer.data, status=status.HTTP_200_OK)