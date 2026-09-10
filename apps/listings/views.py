from drf_spectacular.utils import extend_schema
from rest_framework import status, viewsets
#from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response
from datetime import timedelta
from django.utils import timezone
from django.db.models import Q

from .permissions import IsOwnerOrReadOnly, ModelPermissions
from .models import Listing
from .serializers import ListingSerializer




class ListingViewSet(viewsets.ModelViewSet):
    queryset = Listing.objects.all()
    serializer_class = ListingSerializer
    permission_classes = [IsOwnerOrReadOnly]

    @extend_schema(request=ListingSerializer, responses=ListingSerializer)
    def create(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        listing = serializer.save(owner=request.user)
        return Response(self.get_serializer(listing).data, status=status.HTTP_201_CREATED)

    def destroy(self, request, *args, **kwargs):
        listing = self.get_object()
        if listing.deleted_at is not None:
            return Response({"detail": "Listing is already deleted."}, status=status.HTTP_400_BAD_REQUEST)
        listing.is_active = False
        listing.deleted_at = timezone.now()
        listing.save(update_fields=["is_active", "deleted_at"])

        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=["post"], url_path="restore")
    def restore(self, request, *args, **kwargs):
        listing = self.get_object()
        if listing.deleted_at is None:
            return Response({"detail": "This listing is not deleted."}, status=status.HTTP_400_BAD_REQUEST)
        if listing.deleted_at < timezone.now() - timedelta(days=180):
            return Response({"detail": "The restoration period has expired."}, status=status.HTTP_400_BAD_REQUEST)

        listing.is_active = True
        listing.deleted_at = None
        listing.save(update_fields=["is_active", "deleted_at"])

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
        restore_limit = timezone.now() - timedelta(days=180)
        return Listing.objects.filter(Q(is_active=True) | Q(owner=user, deleted_at__gte=restore_limit))