import pytest
from datetime import timedelta

from django.utils import timezone
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from apps.users.models import BookingUser
from apps.bookings.services import create_booking


def get_future_booking_dates():
    """
    Return future dates for open booking tests.
    """
    now = timezone.now()

    date_start = (now + timedelta(days=10)).replace(
        hour=14,
        minute=0,
        second=0,
        microsecond=0,
    )
    date_end = (now + timedelta(days=12)).replace(
        hour=11,
        minute=0,
        second=0,
        microsecond=0,
    )

    return date_start, date_end


@pytest.fixture
def api_client():
    """
    Create and return an API client for testing HTTP requests.
    """
    return APIClient()


def test_register_user(api_client, db):
    """
    Check that a new user can register through the API.
    """
    url = reverse("users-register")

    data = {
        "first_name": "New",
        "last_name": "User",
        "email": "newuser@example.com",
        "phone": "+491111111111",
        "password": "TestPassword1!",
    }

    response = api_client.post(url, data, format="json")

    assert response.status_code == status.HTTP_201_CREATED

    assert response.data["first_name"] == "New"
    assert response.data["last_name"] == "User"
    assert response.data["email"] == "newuser@example.com"
    assert response.data["phone"] == "+491111111111"

    assert BookingUser.objects.filter(
        email="newuser@example.com"
    ).exists()


def test_register_user_rejects_duplicate_email(api_client, user):
    """
    Check that registration is rejected when the email already exists.
    """
    url = reverse("users-register")

    data = {
        "first_name": "Another",
        "last_name": "User",
        "email": user.email,
        "phone": "+492222222222",
        "password": "TestPassword1!",
    }

    response = api_client.post(url, data, format="json")

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "email" in response.data


def test_get_current_user(api_client, user):
    """
    Check that an authenticated user can get their own profile.
    """
    api_client.force_authenticate(user=user)

    url = reverse("users-me")

    response = api_client.get(url)

    assert response.status_code == status.HTTP_200_OK

    assert response.data["first_name"] == user.first_name
    assert response.data["last_name"] == user.last_name
    assert response.data["email"] == user.email
    assert response.data["phone"] == user.phone
    assert response.data["is_active"] is True


def test_get_current_user_requires_authentication(api_client):
    """
    Check that an unauthenticated user cannot access their profile.
    """
    url = reverse("users-me")

    response = api_client.get(url)

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_update_current_user(api_client, user):
    """
    Check that an authenticated user can update their own profile.
    """
    api_client.force_authenticate(user=user)

    url = reverse("users-me")

    data = {
        "first_name": "Updated",
        "last_name": "Name",
        "phone": "+493333333333",
    }

    response = api_client.patch(url, data, format="json")

    assert response.status_code == status.HTTP_200_OK

    assert response.data["first_name"] == "Updated"
    assert response.data["last_name"] == "Name"
    assert response.data["phone"] == "+493333333333"

    user.refresh_from_db()

    assert user.first_name == "Updated"
    assert user.last_name == "Name"
    assert user.phone == "+493333333333"


def test_update_current_user_cannot_change_email(api_client, user):
    """
    Check that the user's email cannot be changed through the profile API.
    """
    api_client.force_authenticate(user=user)
    url = reverse("users-me")
    old_email = user.email
    data = {"email": "changed@example.com"}

    response = api_client.patch(url, data, format="json")
    assert response.status_code == status.HTTP_200_OK

    user.refresh_from_db()
    assert user.email == old_email


def test_update_current_user_cannot_change_is_active(api_client, user):
    """
    Check that the user cannot change their own active status.
    """
    api_client.force_authenticate(user=user)
    url = reverse("users-me")

    response = api_client.patch(
        url,
        {"is_active": False},
        format="json",
    )

    assert response.status_code == status.HTTP_200_OK

    user.refresh_from_db()
    assert user.is_active is True


def test_delete_current_user_deactivates_user(api_client, user):
    """
    Check that deleting the current user deactivates the account.
    """
    api_client.force_authenticate(user=user)

    url = reverse("users-me")

    response = api_client.delete(url)

    assert response.status_code == status.HTTP_204_NO_CONTENT

    user.refresh_from_db()

    assert user.is_active is False


def test_delete_current_user_requires_authentication(api_client):
    """
    Check that an unauthenticated user cannot deactivate an account.
    """
    url = reverse("users-me")

    response = api_client.delete(url)

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_delete_current_user_rejected_when_tenant_has_open_booking(
    api_client,
    user,
    booking_listing,
):
    """
    Check that a tenant with an open booking
    cannot deactivate their account.
    """
    date_start, date_end = get_future_booking_dates()

    create_booking(
        tenant=user,
        listing_id=booking_listing.id,
        date_start=date_start,
        date_end=date_end,
    )

    api_client.force_authenticate(user=user)

    url = reverse("users-me")

    response = api_client.delete(url)

    assert response.status_code == status.HTTP_400_BAD_REQUEST

    user.refresh_from_db()

    assert user.is_active is True


def test_delete_current_user_rejected_when_owner_has_open_booking(
    api_client,
    user,
    booking_owner,
    listing,
):
    """
    Check that a listing owner with an open booking
    cannot deactivate their account.
    """
    date_start, date_end = get_future_booking_dates()

    create_booking(
        tenant=booking_owner,
        listing_id=listing.id,
        date_start=date_start,
        date_end=date_end,
    )

    api_client.force_authenticate(user=user)

    url = reverse("users-me")

    response = api_client.delete(url)

    assert response.status_code == status.HTTP_400_BAD_REQUEST

    user.refresh_from_db()

    assert user.is_active is True


def test_delete_current_user_deactivates_owned_listings(
    api_client,
    user,
    listing,
):
    """
    Check that deactivating a user also deactivates
    all active listings owned by that user.
    """
    assert listing.owner == user
    assert listing.is_active is True

    api_client.force_authenticate(user=user)

    url = reverse("users-me")

    response = api_client.delete(url)

    assert response.status_code == status.HTTP_204_NO_CONTENT

    user.refresh_from_db()
    listing.refresh_from_db()

    assert user.is_active is False
    assert listing.is_active is False