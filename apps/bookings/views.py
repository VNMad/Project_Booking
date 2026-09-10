from rest_framework import status, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema

from .serializers import BookingCreateSerializer, BookingSerializer
from .services import create_booking


class BookingViewSet(viewsets.GenericViewSet):
    permission_classes = [IsAuthenticated]

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