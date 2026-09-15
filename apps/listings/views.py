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
from .permissions import IsOwnerOrReadOnly, ModelPermissions
from .models import Listing, Photo
from .serializers import ListingSerializer, PhotoSerializer
from .filters import ListingFilter




class ListingViewSet(viewsets.ModelViewSet):
    queryset = Listing.objects.all()
    serializer_class = ListingSerializer
    permission_classes = [IsOwnerOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = ListingFilter
    search_fields = ["title", "description", "city", "district"]
    ordering_fields = ["price_per_night", "created_at"]
    ordering = ["-created_at"]

    @extend_schema(request=ListingSerializer, responses=ListingSerializer)
    def create(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        listing = serializer.save(owner=request.user)
        listing = self.get_queryset().get(pk=listing.pk)
        return Response(self.get_serializer(listing).data, status=status.HTTP_201_CREATED)

    def destroy(self, request, *args, **kwargs):
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

    @action(detail=True, methods=["post"], url_path="restore")
    def restore(self, request, *args, **kwargs):
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

    def update(self, request, *args, **kwargs):
        listing = self.get_object()
        if listing.deleted_at is not None:
            return Response({"detail": "Deleted listing cannot be edited."}, status=status.HTTP_400_BAD_REQUEST)
        return super().update(request, *args, **kwargs)

    def partial_update(self, request, *args, **kwargs):
        listing = self.get_object()
        if listing.deleted_at is not None:
            return Response({"detail": "Deleted listing cannot be edited."}, status=status.HTTP_400_BAD_REQUEST)
        return super().partial_update(request, *args, **kwargs)

    def get_queryset(self):
        user = self.request.user
        queryset = Listing.objects.annotate(reviews_count=Count("bookings__review", distinct=True),
                                            average_cleanliness=Avg("bookings__review__cleanliness_rating"),
                                            average_location=Avg("bookings__review__location_rating"))
        restore_limit = timezone.now() - timedelta(days=LISTING_SOFT_DELETE_DAYS)
        if not user.is_authenticated:
            return queryset.filter(is_active=True)

        return queryset.filter(Q(is_active=True) | Q(owner=user, deleted_at__gte=restore_limit))


class PhotoViewSet(viewsets.ModelViewSet):
    serializer_class = PhotoSerializer
    permission_classes = [IsOwnerOrReadOnly]

    def get_queryset(self):
        return Photo.objects.select_related("listing").all()

    def perform_create(self, serializer):
        listing = serializer.validated_data["listing"]

        if listing.owner_id != self.request.user.id:
            raise PermissionDenied("You can add photos only to your own listing.")

        if listing.photos.count() >= LISTING_MAX_PHOTOS:
            raise serializers.ValidationError(f"A listing cannot have more than {LISTING_MAX_PHOTOS} photos.")

        serializer.save()