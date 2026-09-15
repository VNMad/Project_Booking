from drf_spectacular.utils import extend_schema
from rest_framework import status, viewsets, serializers, filters
#from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied
from datetime import timedelta
from django.utils import timezone
from django.db.models import Q, Avg, Count
from django_filters.rest_framework import DjangoFilterBackend

from core.models import BookingStatus
from core.constants import LISTING_SOFT_DELETE_DAYS, LISTING_MAX_PHOTOS
from .permissions import IsOwnerOrReadOnly
from .models import Listing, Photo
from .serializers import ListingSerializer, PhotoSerializer
from .filters import ListingFilter




class ListingViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing rental listings.
    Provides listing creation, retrieval, updating, soft deletion,
    restoration, filtering, searching, ordering, and pagination.
    Public users can view active listings. Listing owners can create,
    update, delete, and restore their own listings.
    """
    queryset = Listing.objects.all()
    serializer_class = ListingSerializer
    permission_classes = [IsOwnerOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = ListingFilter
    search_fields = ["title", "description", "city", "district"]
    ordering_fields = ["price_per_night", "created_at"]
    ordering = ["-created_at"]


    @extend_schema(request=ListingSerializer, responses=ListingSerializer, summary="Create a listing",
                   description=("Create a new rental listing. The authenticated user becomes "
                                "the owner of the listing. Review statistics are calculated "
                                "automatically and returned in the response."))
    def create(self, request):
        """ Create a new rental listing owned by the authenticated user. """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        listing = serializer.save(owner=request.user)
        listing = self.get_queryset().get(pk=listing.pk)
        return Response(self.get_serializer(listing).data, status=status.HTTP_201_CREATED)


    @extend_schema(responses=None, summary="Delete a listing",
                   description=("Soft-delete a listing owned by the authenticated user. "
                                "A listing with pending or confirmed bookings cannot be deleted. "
                                "The listing remains restorable during the configured "
                                "soft-delete period."))
    def destroy(self, request, *args, **kwargs):
        """
        Soft-delete a listing.
        A listing cannot be deleted if it already has pending or
        confirmed bookings.
        """
        listing = self.get_object()
        if listing.deleted_at is not None:
            return Response({"detail": "Listing is already deleted."}, status=status.HTTP_400_BAD_REQUEST)
        if listing.bookings.filter(status__in=[BookingStatus.PENDING, BookingStatus.CONFIRMED]).exists():
            return Response({"detail": "Listing cannot be deleted because it has active."},
                            status=status.HTTP_400_BAD_REQUEST)
        listing.is_active = False
        listing.deleted_at = timezone.now()
        listing.save(update_fields=["is_active", "deleted_at"])

        return Response(status=status.HTTP_204_NO_CONTENT)


    @extend_schema(responses=ListingSerializer, summary="Restore a deleted listing",
                   description=("Restore a soft-deleted listing. Restoration is available only "
                               f"within {LISTING_SOFT_DELETE_DAYS} days after deletion."))
    @action(detail=True, methods=["post"], url_path="restore")
    def restore(self, request, *args, **kwargs):
        """ Restore a soft-deleted listing within the allowed restoration period. """
        listing = self.get_object()
        if listing.deleted_at is None:
            return Response({"detail": "This listing is not deleted."}, status=status.HTTP_400_BAD_REQUEST)
        if listing.deleted_at < timezone.now() - timedelta(days=LISTING_SOFT_DELETE_DAYS):
            return Response({"detail": "The restoration period has expired."}, status=status.HTTP_400_BAD_REQUEST)

        listing.is_active = True
        listing.deleted_at = None
        listing.save(update_fields=["is_active", "deleted_at"])
        listing = self.get_queryset().get(pk=listing.pk)

        return Response(self.get_serializer(listing).data, status=status.HTTP_200_OK)


    @extend_schema(request=ListingSerializer, responses=ListingSerializer, summary="Update a listing",
                   description=("Fully update a listing owned by the authenticated user. "
                                "Deleted listings cannot be edited."))
    def update(self, request, *args, **kwargs):
        """
        Fully update an active listing.
        Deleted listings cannot be edited.
        """
        listing = self.get_object()
        if listing.deleted_at is not None:
            return Response({"detail": "Deleted listing cannot be edited."}, status=status.HTTP_400_BAD_REQUEST)
        return super().update(request, *args, **kwargs)


    @extend_schema(request=ListingSerializer, responses=ListingSerializer, summary="Partially update a listing",
                   description=("Partially update a listing owned by the authenticated user. "
                                "Deleted listings cannot be edited."))
    def partial_update(self, request, *args, **kwargs):
        """
        Partially update an active listing.
        Deleted listings cannot be edited.
        """
        listing = self.get_object()
        if listing.deleted_at is not None:
            return Response({"detail": "Deleted listing cannot be edited."}, status=status.HTTP_400_BAD_REQUEST)
        return super().partial_update(request, *args, **kwargs)

    def get_queryset(self):
        """
        Return listings available to the current user.
        Unauthenticated users can see active listings only.
        Authenticated users can also see their own recently deleted
        listings while the restoration period is still active.
        The queryset includes review count and average rating annotations.
        """
        user = self.request.user
        queryset = Listing.objects.annotate(reviews_count=Count("bookings__review", distinct=True),
                                            average_cleanliness=Avg("bookings__review__cleanliness_rating"),
                                            average_location=Avg("bookings__review__location_rating"))
        restore_limit = timezone.now() - timedelta(days=LISTING_SOFT_DELETE_DAYS)
        if not user.is_authenticated:
            return queryset.filter(is_active=True)

        return queryset.filter(Q(is_active=True) | Q(owner=user, deleted_at__gte=restore_limit))


class PhotoViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing photos associated with rental listings.
    Users can add photos only to listings they own. The number of photos
    per listing is limited by LISTING_MAX_PHOTOS.
    """
    serializer_class = PhotoSerializer
    permission_classes = [IsOwnerOrReadOnly]

    def get_queryset(self):
        """ Return listing photos with their related listing loaded. """
        return Photo.objects.select_related("listing").all()

    def perform_create(self, serializer):
        """
        Validate listing ownership and the maximum photo limit before creating a photo.
        """
        listing = serializer.validated_data["listing"]

        if listing.owner_id != self.request.user.id:
            raise PermissionDenied("You can add photos only to your own listing.")

        if listing.photos.count() >= LISTING_MAX_PHOTOS:
            raise serializers.ValidationError(f"A listing cannot have more than {LISTING_MAX_PHOTOS} photos.")

        serializer.save()