from rest_framework import serializers, status, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.exceptions import NotFound
from drf_spectacular.utils import extend_schema
from django.db.models import Q
from django.core.exceptions import ValidationError as DjangoValidationError

from .models import Booking
from .serializers import BookingCreateSerializer, BookingSerializer
from .services import create_booking, confirm_booking, reject_booking, cancel_booking, BookingNotFoundError, \
    complete_booking_if_finished


class BookingViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = BookingSerializer

    def get_queryset(self):
        user = self.request.user
        return Booking.objects.filter(Q(tenant=user) | Q(listing__owner=user)).distinct()

    def _handle_service_error(self, exc):
        if isinstance(exc, BookingNotFoundError):
            raise NotFound({"detail": str(exc)})
        if isinstance(exc, DjangoValidationError):
            raise serializers.ValidationError({"detail": exc.messages})
        raise exc

    @extend_schema(request=BookingCreateSerializer, responses=BookingSerializer)
    def create(self, request):
        serializer = BookingCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            booking = create_booking(
                tenant=request.user,
                listing_id=serializer.validated_data["listing"].id,
                date_start=serializer.validated_data["date_start"],
                date_end=serializer.validated_data["date_end"],
            )
        except (BookingNotFoundError, DjangoValidationError) as exc:
            self._handle_service_error(exc)

        return Response(BookingSerializer(booking).data, status=status.HTTP_201_CREATED)

    def retrieve(self, request, pk=None):
        booking = self.get_object()
        booking = complete_booking_if_finished(booking)
        serializer = BookingSerializer(booking)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(request=None, responses=BookingSerializer)
    @action(detail=True, methods=["post"], url_path="confirm")
    def confirm(self, request, pk=None):
        try:
            booking = confirm_booking(booking_id=pk, owner=request.user)
        except (BookingNotFoundError, DjangoValidationError) as exc:
            self._handle_service_error(exc)
        return Response(BookingSerializer(booking).data, status=status.HTTP_200_OK)

    @extend_schema(request=None, responses=BookingSerializer)
    @action(detail=True, methods=["post"], url_path="reject")
    def reject(self, request, pk=None):
        try:
            booking = reject_booking(booking_id=pk, owner=request.user)
        except (BookingNotFoundError, DjangoValidationError) as exc:
            self._handle_service_error(exc)
        return Response(BookingSerializer(booking).data, status=status.HTTP_200_OK)


    @extend_schema(request=None, responses=BookingSerializer)
    @action(detail=True, methods=["post"], url_path="cancel")
    def cancel(self, request, pk=None):
        try:
            booking = cancel_booking(booking_id=pk, tenant=request.user)
        except (BookingNotFoundError, DjangoValidationError) as exc:
            self._handle_service_error(exc)

        return Response(BookingSerializer(booking).data, status=status.HTTP_200_OK)

    def update(self, request, *args, **kwargs):
        return Response({"detail": "Booking cannot be edited."}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

    def partial_update(self, request, *args, **kwargs):
        return Response({"detail": "Booking cannot be edited."}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

    def destroy(self, request, *args, **kwargs):
        return Response({"detail": "Booking cannot be deleted."}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
