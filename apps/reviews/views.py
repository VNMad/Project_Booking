from django.core.exceptions import ValidationError as DjangoValidationError

from rest_framework import serializers, status, viewsets
from rest_framework.exceptions import NotFound
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Review
from .permissions import IsReviewOwner
from .serializers import ReviewSerializer, ReviewCreateSerializer
from .services import create_review


class ReviewViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, IsReviewOwner]
    #serializer_class = ReviewSerializer

    def get_queryset(self):
        user = self.request.user
        return Review.objects.filter(booking__tenant=user).select_related("booking")

    def get_serializer_class(self):
        if self.action == "create":
            return ReviewCreateSerializer
        return ReviewSerializer

    def _handle_service_error(self, exc):
        if isinstance(exc, DjangoValidationError):
            raise serializers.ValidationError({"detail": exc.messages})
        raise exc

    def create(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            review = create_review(booking=serializer.validated_data["booking"],
                                   user=request.user,
                                   cleanliness_rating=serializer.validated_data["cleanliness_rating"],
                                   location_rating=serializer.validated_data["location_rating"],
                                   comment=serializer.validated_data["comment"],
            )
        except DjangoValidationError as exc:
            self._handle_service_error(exc)

        return Response(ReviewSerializer(review).data, status=status.HTTP_201_CREATED)