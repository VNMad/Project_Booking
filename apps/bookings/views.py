from rest_framework import status, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema
from django.db.models import Q

from .models import Booking
from .serializers import BookingCreateSerializer, BookingSerializer
from .services import create_booking


class BookingViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Booking.objects.filter(Q(tenant=user) | Q(listing__owner=user)).distinct()

    @extend_schema(request=BookingCreateSerializer, responses=BookingSerializer)

    def create(self, request):
        serializer = BookingCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        booking = create_booking(
            tenant=request.user,
            listing_id=serializer.validated_data["listing"].id,
            date_start=serializer.validated_data["date_start"],
            date_end=serializer.validated_data["date_end"],
        )

        return Response(BookingSerializer(booking).data, status=status.HTTP_201_CREATED)

    def list(self, request):
        queryset = self.get_queryset()
        serializer = BookingSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def retrieve(self, request, pk=None):
        booking = self.get_object()
        serializer = BookingSerializer(booking)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def update(self, request, *args, **kwargs):
        return Response({"detail": "Booking cannot be edited."}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

    def partial_update(self, request, *args, **kwargs):
        return Response({"detail": "Booking cannot be edited."}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

    def destroy(self, request, *args, **kwargs):
        return Response({"detail": "Booking cannot be deleted."}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

