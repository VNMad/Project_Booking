from types import SimpleNamespace

import pytest
from django.contrib.auth.models import AnonymousUser

from apps.reviews.models import Review
from apps.reviews.permissions import IsReviewOwner


@pytest.mark.parametrize(
    "method",
    ["GET", "HEAD", "OPTIONS"],
)
def test_review_permission_allows_safe_methods_for_anonymous_user(method):
    """
    Check that safe HTTP methods are allowed without authentication.
    """
    permission = IsReviewOwner()

    request = SimpleNamespace(
        method=method,
        user=AnonymousUser(),
    )
    view = SimpleNamespace()

    assert permission.has_permission(request, view) is True


@pytest.mark.parametrize(
    "method",
    ["POST", "PUT", "PATCH", "DELETE"],
)
def test_review_permission_allows_unsafe_methods_for_authenticated_user(
    user,
    method,
):
    """
    Check that authenticated users pass the general permission check
    for unsafe HTTP methods.
    """
    permission = IsReviewOwner()

    request = SimpleNamespace(
        method=method,
        user=user,
    )
    view = SimpleNamespace()

    assert permission.has_permission(request, view) is True


@pytest.mark.parametrize(
    "method",
    ["POST", "PUT", "PATCH", "DELETE"],
)
def test_review_permission_rejects_unsafe_methods_for_anonymous_user(method):
    """
    Check that anonymous users cannot use unsafe HTTP methods.
    """
    permission = IsReviewOwner()

    request = SimpleNamespace(
        method=method,
        user=AnonymousUser(),
    )
    view = SimpleNamespace()

    assert permission.has_permission(request, view) is False


@pytest.mark.parametrize(
    "method",
    ["GET", "HEAD", "OPTIONS"],
)
def test_review_object_permission_allows_safe_methods_for_non_owner(
    booking_owner,
    completed_booking,
    method,
):
    """
    Check that safe HTTP methods are allowed even for users
    who do not own the review.
    """
    review = Review.objects.create(
        booking=completed_booking,
        cleanliness_rating=5,
        location_rating=4,
        comment="Great stay.",
    )

    permission = IsReviewOwner()

    request = SimpleNamespace(
        method=method,
        user=booking_owner,
    )
    view = SimpleNamespace()

    assert permission.has_object_permission(
        request,
        view,
        review,
    ) is True


@pytest.mark.parametrize(
    "method",
    ["PUT", "PATCH", "DELETE"],
)
def test_review_object_permission_allows_tenant(
    user,
    completed_booking,
    method,
):
    """
    Check that the booking tenant can modify or delete their review.
    """
    review = Review.objects.create(
        booking=completed_booking,
        cleanliness_rating=5,
        location_rating=4,
        comment="Great stay.",
    )

    permission = IsReviewOwner()

    request = SimpleNamespace(
        method=method,
        user=user,
    )
    view = SimpleNamespace()

    assert permission.has_object_permission(
        request,
        view,
        review,
    ) is True


@pytest.mark.parametrize(
    "method",
    ["PUT", "PATCH", "DELETE"],
)
def test_review_object_permission_rejects_non_tenant(
    booking_owner,
    completed_booking,
    method,
):
    """
    Check that another authenticated user cannot modify
    or delete someone else's review.
    """
    review = Review.objects.create(
        booking=completed_booking,
        cleanliness_rating=5,
        location_rating=4,
        comment="Great stay.",
    )

    permission = IsReviewOwner()

    request = SimpleNamespace(
        method=method,
        user=booking_owner,
    )
    view = SimpleNamespace()

    assert permission.has_object_permission(
        request,
        view,
        review,
    ) is False