from django.core.exceptions import ValidationError as DjangoValidationError
from drf_spectacular.utils import extend_schema
from rest_framework import serializers, status, viewsets
from rest_framework.response import Response

from .models import Review
from .permissions import IsReviewOwner
from .serializers import ReviewSerializer, ReviewCreateSerializer
from .services import create_review


class ReviewViewSet(viewsets.ModelViewSet):
    """
    ViewSet for creating and retrieving reviews.
    Reviews are associated with completed bookings.
    Access to reviews is controlled by IsReviewOwner permission.
    """
    permission_classes = [IsReviewOwner]

    def get_queryset(self):
        """
        Return reviews with their related bookings loaded.
        select_related() is used to avoid additional database queries
        when accessing the booking associated with a review.
        """
        return Review.objects.select_related("booking")

    def get_serializer_class(self):
        """
        Return the appropriate serializer for the current action.
        ReviewCreateSerializer is used when creating a review.
        ReviewSerializer is used for other actions.
        """
        if self.action == "create":
            return ReviewCreateSerializer
        return ReviewSerializer

    def _handle_service_error(self, exc):
        """
        Convert Django validation errors raised by the service layer into DRF validation errors.
        """
        if isinstance(exc, DjangoValidationError):
            raise serializers.ValidationError({"detail": exc.messages})
        raise exc


    @extend_schema(request=ReviewCreateSerializer, responses=ReviewSerializer, summary="Create a review",
                   description=("Create a review for a booking. "
                                "The booking must satisfy the business rules defined "
                                "by the review service. "
                                "The review contains separate cleanliness and location "
                                "ratings from 1 to 5 and an optional comment."))
    def create(self, request):
        """ Create a review for the authenticated user. """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            review = create_review(booking=serializer.validated_data["booking"],
                                   user=request.user,
                                   cleanliness_rating=serializer.validated_data["cleanliness_rating"],
                                   location_rating=serializer.validated_data["location_rating"],
                                   comment=serializer.validated_data.get("comment", ""))
        except DjangoValidationError as exc:
            self._handle_service_error(exc)

        return Response(ReviewSerializer(review).data, status=status.HTTP_201_CREATED)