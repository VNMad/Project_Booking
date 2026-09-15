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
    """
    ViewSet for user registration and authenticated user profile management.
    Provides endpoints for:
    - registering a new user;
    - retrieving the current user's profile;
    - updating the current user's profile;
    - deactivating the current user's account.
    """
    permission_classes = [AllowAny]

    def get_permissions(self):
        """
        Return permissions according to the requested user action.
        Registration is available to unauthenticated users.
        Profile operations require authentication.
        """
        if self.action in ["me", "update_me", "delete_me"]:
            return [IsAuthenticated()]

        return [AllowAny()]

    @extend_schema(request=RegisterSerializer, responses=UserSerializer,
                   summary="Register a new user",
                   description=("Create a new user account using an email address, "
                                "personal information, phone number, and password. "
                                "The email address is used as the login identifier.")
                   )
    @action(
        detail=False,
        methods=["post"],
        url_path="register",
        url_name="register",
    )
    def register(self, request):
        """
        Register a new user account.
        Validates the submitted registration data and creates
        a new user using the custom user manager.
        """
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        return Response(UserSerializer(user).data, status=status.HTTP_201_CREATED)

    @extend_schema(responses=UserSerializer, summary="Get current user",
        description="Return the profile of the currently authenticated user.")
    @action(
        detail=False,
        methods=["get"],
        url_path="me",
        url_name="me",
    )
    def me(self, request):
        """ Return the currently authenticated user's profile. """
        serializer = UserSerializer(request.user)

        return Response(serializer.data, status=status.HTTP_200_OK)

    @me.mapping.patch
    @extend_schema(request=UserSerializer, responses=UserSerializer, summary="Update current user",
                   description=("Partially update the profile of the currently authenticated "
                                "user. Email address, account status, and timestamps are read-only."))
    def update_me(self, request):
        """ Partially update the currently authenticated user's profile. """
        serializer = UserSerializer(request.user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_200_OK)

    @me.mapping.delete
    @extend_schema(responses=None, summary="Deactivate current user account",
                                   description=("Deactivate the currently authenticated user's account. "
                                                "The account cannot be deactivated while the user has "
                                                "pending or confirmed bookings that have not yet ended. "
                                                "The user's active listings are also deactivated."))
    def delete_me(self, request):
        """
        Deactivate the currently authenticated user's account.
        The account is not physically deleted. The user is marked
        as inactive and active listings owned by the user are deactivated.
        Deactivation is rejected when open bookings exist.
        """
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