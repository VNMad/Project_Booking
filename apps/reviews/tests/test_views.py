from django.urls import reverse

from apps.reviews.models import Review
from core.models import BookingStatus


def test_review_list_is_available_for_anonymous_user(
    api_client,
    completed_booking,
):
    """
    Check that an anonymous user can view the review list.
    """
    Review.objects.create(
        booking=completed_booking,
        cleanliness_rating=5,
        location_rating=4,
        comment="Great stay.",
    )

    url = reverse("review-list")
    response = api_client.get(url)

    assert response.status_code == 200
    assert response.data["count"] == 1
    assert len(response.data["results"]) == 1


def test_review_detail_is_available_for_anonymous_user(
    api_client,
    completed_booking,
):
    """
    Check that an anonymous user can retrieve a review.
    """
    review = Review.objects.create(
        booking=completed_booking,
        cleanliness_rating=5,
        location_rating=4,
        comment="Great stay.",
    )

    url = reverse(
        "review-detail",
        kwargs={"pk": review.id},
    )
    response = api_client.get(url)

    assert response.status_code == 200
    assert response.data["id"] == str(review.id)
    assert response.data["cleanliness_rating"] == 5
    assert response.data["location_rating"] == 4
    assert response.data["comment"] == "Great stay."


def test_authenticated_tenant_can_create_review(
    api_client,
    user,
    completed_booking,
):
    """
    Check that the booking tenant can create a review.
    """
    api_client.force_authenticate(user=user)

    url = reverse("review-list")
    data = {
        "booking": str(completed_booking.id),
        "cleanliness_rating": 5,
        "location_rating": 4,
        "comment": "Very clean apartment.",
    }

    response = api_client.post(
        url,
        data,
        format="json",
    )

    assert response.status_code == 201
    assert Review.objects.count() == 1

    review = Review.objects.get()

    assert review.booking == completed_booking
    assert review.cleanliness_rating == 5
    assert review.location_rating == 4
    assert review.comment == "Very clean apartment."


def test_anonymous_user_cannot_create_review(
    api_client,
    completed_booking,
):
    """
    Check that authentication is required to create a review.
    """
    url = reverse("review-list")
    data = {
        "booking": str(completed_booking.id),
        "cleanliness_rating": 5,
        "location_rating": 4,
        "comment": "Great stay.",
    }

    response = api_client.post(
        url,
        data,
        format="json",
    )

    assert response.status_code == 401
    assert Review.objects.count() == 0


def test_non_tenant_cannot_create_review(
    api_client,
    booking_owner,
    completed_booking,
):
    """
    Check that a user who did not make the booking
    cannot create a review for it.
    """
    api_client.force_authenticate(user=booking_owner)

    url = reverse("review-list")
    data = {
        "booking": str(completed_booking.id),
        "cleanliness_rating": 5,
        "location_rating": 4,
        "comment": "Unauthorized review.",
    }

    response = api_client.post(
        url,
        data,
        format="json",
    )

    assert response.status_code == 400
    assert Review.objects.count() == 0


def test_review_cannot_be_created_for_non_completed_booking(
    api_client,
    user,
    completed_booking,
):
    """
    Check that a review cannot be created
    for a booking that is not completed.
    """
    completed_booking.status = BookingStatus.PENDING
    completed_booking.save(update_fields=["status"])

    api_client.force_authenticate(user=user)

    url = reverse("review-list")
    data = {
        "booking": str(completed_booking.id),
        "cleanliness_rating": 5,
        "location_rating": 4,
        "comment": "Booking is not completed.",
    }

    response = api_client.post(
        url,
        data,
        format="json",
    )

    assert response.status_code == 400
    assert Review.objects.count() == 0


def test_review_creation_rejects_invalid_cleanliness_rating(
    api_client,
    user,
    completed_booking,
):
    """
    Check that an invalid cleanliness rating is rejected.
    """
    api_client.force_authenticate(user=user)

    url = reverse("review-list")
    data = {
        "booking": str(completed_booking.id),
        "cleanliness_rating": 6,
        "location_rating": 4,
        "comment": "Invalid rating.",
    }

    response = api_client.post(
        url,
        data,
        format="json",
    )

    assert response.status_code == 400
    assert "cleanliness_rating" in response.data
    assert Review.objects.count() == 0


def test_review_creation_rejects_invalid_location_rating(
    api_client,
    user,
    completed_booking,
):
    """
    Check that an invalid location rating is rejected.
    """
    api_client.force_authenticate(user=user)

    url = reverse("review-list")
    data = {
        "booking": str(completed_booking.id),
        "cleanliness_rating": 5,
        "location_rating": 0,
        "comment": "Invalid rating.",
    }

    response = api_client.post(
        url,
        data,
        format="json",
    )

    assert response.status_code == 400
    assert "location_rating" in response.data
    assert Review.objects.count() == 0


def test_duplicate_review_cannot_be_created(
    api_client,
    user,
    completed_booking,
):
    """
    Check that only one review can be created per booking.
    """
    Review.objects.create(
        booking=completed_booking,
        cleanliness_rating=5,
        location_rating=5,
        comment="First review.",
    )

    api_client.force_authenticate(user=user)

    url = reverse("review-list")
    data = {
        "booking": str(completed_booking.id),
        "cleanliness_rating": 4,
        "location_rating": 4,
        "comment": "Second review.",
    }

    response = api_client.post(
        url,
        data,
        format="json",
    )

    assert response.status_code == 400
    assert Review.objects.count() == 1


def test_tenant_can_update_review(
    api_client,
    user,
    completed_booking,
):
    """
    Check that the booking tenant can update their review.
    """
    review = Review.objects.create(
        booking=completed_booking,
        cleanliness_rating=4,
        location_rating=4,
        comment="Good stay.",
    )

    api_client.force_authenticate(user=user)

    url = reverse(
        "review-detail",
        kwargs={"pk": review.id},
    )
    data = {
        "cleanliness_rating": 5,
        "comment": "Excellent stay.",
    }

    response = api_client.patch(
        url,
        data,
        format="json",
    )

    assert response.status_code == 200

    review.refresh_from_db()

    assert review.cleanliness_rating == 5
    assert review.location_rating == 4
    assert review.comment == "Excellent stay."


def test_non_tenant_cannot_update_review(
    api_client,
    booking_owner,
    completed_booking,
):
    """
    Check that another authenticated user
    cannot update someone else's review.
    """
    review = Review.objects.create(
        booking=completed_booking,
        cleanliness_rating=5,
        location_rating=4,
        comment="Great stay.",
    )

    api_client.force_authenticate(user=booking_owner)

    url = reverse(
        "review-detail",
        kwargs={"pk": review.id},
    )
    data = {
        "cleanliness_rating": 1,
        "comment": "Changed comment.",
    }

    response = api_client.patch(
        url,
        data,
        format="json",
    )

    assert response.status_code == 403

    review.refresh_from_db()

    assert review.cleanliness_rating == 5
    assert review.comment == "Great stay."


def test_tenant_can_delete_review(
    api_client,
    user,
    completed_booking,
):
    """
    Check that the booking tenant can delete their review.
    """
    review = Review.objects.create(
        booking=completed_booking,
        cleanliness_rating=5,
        location_rating=4,
        comment="Great stay.",
    )

    api_client.force_authenticate(user=user)

    url = reverse(
        "review-detail",
        kwargs={"pk": review.id},
    )

    response = api_client.delete(url)

    assert response.status_code == 204
    assert Review.objects.filter(id=review.id).exists() is False


def test_non_tenant_cannot_delete_review(
    api_client,
    booking_owner,
    completed_booking,
):
    """
    Check that another authenticated user
    cannot delete someone else's review.
    """
    review = Review.objects.create(
        booking=completed_booking,
        cleanliness_rating=5,
        location_rating=4,
        comment="Great stay.",
    )

    api_client.force_authenticate(user=booking_owner)

    url = reverse(
        "review-detail",
        kwargs={"pk": review.id},
    )

    response = api_client.delete(url)

    assert response.status_code == 403
    assert Review.objects.filter(id=review.id).exists() is True


def test_create_review_without_comment(
    api_client,
    user,
    completed_booking,
):
    """
    Check that a review can be created without a comment.
    """
    api_client.force_authenticate(user=user)

    url = reverse("review-list")
    data = {
        "booking": str(completed_booking.id),
        "cleanliness_rating": 5,
        "location_rating": 4,
    }

    response = api_client.post(
        url,
        data,
        format="json",
    )

    assert response.status_code == 201

    review = Review.objects.get()

    assert review.comment == ""