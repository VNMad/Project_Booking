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
    """
        ViewSet for managing rental bookings.

        Provides booking creation, retrieval, confirmation, rejection,
        cancellation, and automatic completion of finished bookings.

        Booking updates and deletion are not allowed.
        """
    permission_classes = [IsAuthenticated]
    serializer_class = BookingSerializer

    def get_queryset(self):
        """
        Return bookings available to the authenticated user.
        A user can access bookings where they are either the tenant
        or the owner of the associated listing.
        """
        user = self.request.user
        return Booking.objects.filter(Q(tenant=user) | Q(listing__owner=user)).distinct()

    def _handle_service_error(self, exc):
        """
        Convert service-layer exceptions into appropriate API exceptions.
        BookingNotFoundError is returned as HTTP 404.
        Django validation errors are returned as HTTP 400.
        Other unexpected exceptions are re-raised.
        """
        if isinstance(exc, BookingNotFoundError):
            raise NotFound({"detail": str(exc)})
        if isinstance(exc, DjangoValidationError):
            raise serializers.ValidationError({"detail": exc.messages})
        raise exc


    @extend_schema(request=BookingCreateSerializer, responses=BookingSerializer, summary="Create a booking",
                   description=("Create a new booking for an active rental listing. "
                                "The authenticated user becomes the tenant. "
                                "The booking is created with a pending status and "
                                "property and tenant information is stored as a snapshot."))
    def create(self, request):
        """
        Create a new booking for the authenticated user.
        Booking creation is handled by the service layer to perform
        availability checks, locking, and snapshot creation.
        """
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


    @extend_schema(responses=BookingSerializer, summary="Get a booking",
                   description=("Return a booking accessible to the authenticated user. "
                                "If the booking period has finished, its status may be "
                                "automatically updated to completed."))
    def retrieve(self, request, pk=None):
        """ Return a booking and update its status when the booking period has finished. """
        booking = self.get_object()
        booking = complete_booking_if_finished(booking)
        serializer = BookingSerializer(booking)
        return Response(serializer.data, status=status.HTTP_200_OK)


    @extend_schema(request=None, responses=BookingSerializer, summary="Confirm a booking",
                   description=("Confirm a pending booking as the owner of the associated "
                                "listing. The authenticated user must be the listing owner."))
    @action(detail=True, methods=["post"], url_path="confirm")
    def confirm(self, request, pk=None):
        """ Confirm a booking as the listing owner. """
        try:
            booking = confirm_booking(booking_id=pk, owner=request.user)
        except (BookingNotFoundError, DjangoValidationError) as exc:
            self._handle_service_error(exc)
        return Response(BookingSerializer(booking).data, status=status.HTTP_200_OK)


    @extend_schema(request=None, responses=BookingSerializer, summary="Reject a booking",
                   description=("Reject a pending booking as the owner of the associated "
                                "listing. The authenticated user must be the listing owner."))
    @action(detail=True, methods=["post"], url_path="reject")
    def reject(self, request, pk=None):
        """ Reject a booking as the listing owner. """
        try:
            booking = reject_booking(booking_id=pk, owner=request.user)
        except (BookingNotFoundError, DjangoValidationError) as exc:
            self._handle_service_error(exc)
        return Response(BookingSerializer(booking).data, status=status.HTTP_200_OK)


    @extend_schema(request=None, responses=BookingSerializer, summary="Cancel a booking",
                   description=("Cancel a booking as the tenant who created it. "
                                "The authenticated user must be the tenant of the booking."))
    @action(detail=True, methods=["post"], url_path="cancel")
    def cancel(self, request, pk=None):
        """ Cancel a booking as the tenant. """
        try:
            booking = cancel_booking(booking_id=pk, tenant=request.user)
        except (BookingNotFoundError, DjangoValidationError) as exc:
            self._handle_service_error(exc)

        return Response(BookingSerializer(booking).data, status=status.HTTP_200_OK)

    @extend_schema(summary="Update booking", description="Booking data cannot be edited after creation.",
        request=BookingSerializer, responses=None)
    def update(self, request, *args, **kwargs):
        """ Reject attempts to fully update a booking. """
        return Response({"detail": "Booking cannot be edited."}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

    @extend_schema(summary="Partially update booking", description="Booking data cannot be edited after creation.",
        request=BookingSerializer, responses=None)
    def partial_update(self, request, *args, **kwargs):
        """  Reject attempts to partially update a booking. """
        return Response({"detail": "Booking cannot be edited."}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

    @extend_schema(summary="Delete booking", description="Bookings cannot be deleted.", responses=None)
    def destroy(self, request, *args, **kwargs):
        """ Reject attempts to delete a booking. """
        return Response({"detail": "Booking cannot be deleted."}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
