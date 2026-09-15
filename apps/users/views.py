import logging
from django.db import transaction
from django.utils import timezone

from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema

from apps.bookings.models import Booking
from apps.listings.models import Listing
from core.models import BookingStatus
from .serializers import RegisterSerializer, UserSerializer


logger = logging.getLogger(__name__)

class UserViewSet(viewsets.GenericViewSet):
    permission_classes = [AllowAny]

    def get_permissions(self):
        if self.action in ["me", "update_me", "delete_me"]:
            return [IsAuthenticated()]

        return [AllowAny()]

    @extend_schema(request=RegisterSerializer, responses=UserSerializer)
    @action(
        detail=False,
        methods=["post"],
        url_path="register",
        url_name="register",
    )
    def register(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        return Response(UserSerializer(user).data, status=status.HTTP_201_CREATED)

    @extend_schema(responses=UserSerializer)
    @action(
        detail=False,
        methods=["get"],
        url_path="me",
        url_name="me",
    )
    def me(self, request):
        serializer = UserSerializer(request.user)

        return Response(serializer.data, status=status.HTTP_200_OK)

    @me.mapping.patch
    @extend_schema(request=UserSerializer, responses=UserSerializer)
    def update_me(self, request):
        serializer = UserSerializer(request.user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_200_OK)

    @me.mapping.delete
    @extend_schema(responses=None)
    def delete_me(self, request):
        user = request.user
        now = timezone.now()

        tenant_has_open_booking = Booking.objects.filter(tenant=user, status__in=[BookingStatus.PENDING,
                                                         BookingStatus.CONFIRMED], date_end__gt=now).exists()
        owner_has_open_booking = Booking.objects.filter(listing__owner=user, status__in=[BookingStatus.PENDING,
                                                         BookingStatus.CONFIRMED], date_end__gt=now).exists()
        if tenant_has_open_booking or owner_has_open_booking:
            logger.warning("User %s cannot be deactivated because open bookings exist.", user.id)
            return Response({"detail": (
                                            "You cannot delete your account while "
                                            "you have open bookings.")}, status=status.HTTP_400_BAD_REQUEST)
        with transaction.atomic():
            user.is_active = False
            user.save(update_fields=["is_active"])

            Listing.objects.filter(owner=user, is_active=True).update(is_active=False)

        logger.info("User %s was deactivated successfully.", user.id)
        return Response(status=status.HTTP_204_NO_CONTENT)