from rest_framework import serializers, status, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.exceptions import NotFound
from drf_spectacular.utils import OpenApiParameter, OpenApiTypes, extend_schema
from django.db.models import Q
from django.core.exceptions import ValidationError as DjangoValidationError
from django.utils import timezone

from .models import Booking
from .serializers import BookingCreateSerializer, BookingSerializer
from .services import (create_booking, confirm_booking, reject_booking, cancel_booking, BookingNotFoundError,
                       complete_booking_if_finished)


class BookingViewSet(viewsets.GenericViewSet):
    """
    ViewSet for managing rental bookings.

    Provides booking creation, retrieval, separate booking lists
    for tenants and listing owners, confirmation, rejection,
    cancellation, and automatic completion of finished bookings.

    Booking updates and deletion are not supported.
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


    @extend_schema(responses=BookingSerializer(many=True), summary="Get my trips",
        description=("Return bookings where the authenticated user is the tenant. "
                     "Use the period parameter to filter current/upcoming "
                     "or past trips."),
        parameters=[OpenApiParameter(
                            name="period",
                            type=OpenApiTypes.STR,
                            location=OpenApiParameter.QUERY,
                            required=False,
                            enum=["active", "past"],
                            description=(
                                    "Filter trips by period. "
                                    "'active' returns current and upcoming trips. "
                                    "'past' returns trips whose check-out date has passed. "
                                    "If omitted, all tenant bookings are returned."))])
    @action(detail=False, methods=["get"], url_path="my-trips")
    def my_trips(self, request):
        """
        Return bookings where the authenticated user is the tenant.

        Optional period query parameter:
        - active: current and upcoming trips;
        - past: trips whose check-out date has passed.
        """
        bookings = Booking.objects.filter(tenant=request.user)
        period = request.query_params.get("period")

        if period == "active":
            bookings = bookings.filter(date_end__gte=timezone.now()).order_by("date_start")
        elif period == "past":
            bookings = bookings.filter(date_end__lt=timezone.now()).order_by("-date_end")
        else:
            bookings = bookings.order_by("date_start")
        page = self.paginate_queryset(bookings)

        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(bookings, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


    @extend_schema(responses=BookingSerializer(many=True), summary="Get bookings for my listings",
        description=("Return bookings created by tenants for listings owned "
                     "by the authenticated user."))
    @action(detail=False, methods=["get"], url_path="my-listings")
    def my_listings(self, request):
        """
        Return bookings created for listings owned by the authenticated user.
        """
        bookings = (Booking.objects.filter(listing__owner=request.user).select_related("listing", "tenant")
                    .order_by("-created_at"))
        page = self.paginate_queryset(bookings)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(bookings, many=True)
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

