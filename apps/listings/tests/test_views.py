from django.urls import reverse
from rest_framework import status

from apps.users.models import BookingUser
from apps.listings.models import Listing


def test_list_listings(api_client, user):
    """
    Check that listings can be requested without authentication.
    """
    url = reverse("listings-list")

    response = api_client.get(url)

    assert response.status_code == status.HTTP_200_OK


def test_retrieve_listing(api_client, listing):
    """
    Check that a listing can be retrieved.
    """
    api_client.force_authenticate(user=listing.owner)

    url = reverse(
        "listings-detail",
        kwargs={"pk": listing.id},
    )

    response = api_client.get(url)

    assert response.status_code == status.HTTP_200_OK
    assert response.data["id"] == str(listing.id)
    assert response.data["title"] == listing.title


def test_create_listing(api_client, user):
    """
    Check that an authenticated user can create a listing.
    """
    api_client.force_authenticate(user=user)

    url = reverse("listings-list")

    data = {
        "title": "New apartment",
        "description": "Beautiful apartment in Hamburg.",
        "country": "DE",
        "city": "Hamburg",
        "district": "Altona",
        "street": "New Street",
        "house_number": "15",
        "apartment_number": "7",
        "price_per_night": "120.00",
        "rooms": "2",
    }

    response = api_client.post(
        url,
        data,
        format="json",
    )

    assert response.status_code == status.HTTP_201_CREATED
    assert response.data["title"] == "New apartment"
    assert response.data["city"] == "Hamburg"
    created_listing_id = response.data["id"]
    listing = Listing.objects.get(id=created_listing_id)
    assert listing.owner == user


def test_create_listing_requires_authentication(api_client):
    """
    Check that an unauthenticated user cannot create a listing.
    """
    url = reverse("listings-list")

    data = {
        "title": "New apartment",
        "description": "Test description.",
        "country": "DE",
        "city": "Hamburg",
        "district": "Altona",
        "street": "New Street",
        "house_number": "15",
        "apartment_number": "7",
        "price_per_night": "120.00",
        "rooms": "2",
    }

    response = api_client.post(
        url,
        data,
        format="json",
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_update_listing(api_client, listing):
    """
    Check that the listing owner can update their listing.
    """
    api_client.force_authenticate(user=listing.owner)

    url = reverse(
        "listings-detail",
        kwargs={"pk": listing.id},
    )

    data = {
        "title": "Updated apartment title",
    }

    response = api_client.patch(
        url,
        data,
        format="json",
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.data["title"] == "Updated apartment title"

    listing.refresh_from_db()

    assert listing.title == "Updated apartment title"


def test_update_listing_forbidden_for_other_user(
    api_client,
    listing,
    user,
):
    """
    Check that another user cannot update someone else's listing.
    """
    other_user = user

    if other_user.id == listing.owner_id:
        other_user = BookingUser.objects.create_user(
            email="other@example.com",
            password="TestPassword1!",
            first_name="Other",
            last_name="User",
            phone="+494444444444",
        )

    api_client.force_authenticate(user=other_user)

    url = reverse(
        "listings-detail",
        kwargs={"pk": listing.id},
    )

    response = api_client.patch(
        url,
        {"title": "Hacked title"},
        format="json",
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_delete_listing_soft_deletes_listing(api_client, listing):
    """
    Check that deleting a listing performs a soft delete.
    """
    api_client.force_authenticate(user=listing.owner)

    url = reverse(
        "listings-detail",
        kwargs={"pk": listing.id},
    )

    response = api_client.delete(url)

    assert response.status_code == status.HTTP_204_NO_CONTENT

    listing.refresh_from_db()

    assert listing.is_active is False
    assert listing.deleted_at is not None


def test_delete_listing_forbidden_for_other_user(
    api_client,
    listing,
    user,
):
    """
    Check that another user cannot delete someone else's listing.
    """
    other_user = BookingUser.objects.create_user(
        email="deleteother@example.com",
        password="TestPassword1!",
        first_name="Other",
        last_name="User",
        phone="+495555555555",
    )

    api_client.force_authenticate(user=other_user)

    url = reverse(
        "listings-detail",
        kwargs={"pk": listing.id},
    )

    response = api_client.delete(url)

    assert response.status_code == status.HTTP_403_FORBIDDEN

    listing.refresh_from_db()

    assert listing.is_active is True
    assert listing.deleted_at is None


def test_restore_listing(api_client, listing):
    """
    Check that the owner can restore a recently soft-deleted listing.
    """
    from django.utils import timezone

    listing.is_active = False
    listing.deleted_at = timezone.now()
    listing.save(update_fields=["is_active", "deleted_at"])

    api_client.force_authenticate(user=listing.owner)

    url = reverse(
        "listings-restore",
        kwargs={"pk": listing.id},
    )

    response = api_client.post(url)

    assert response.status_code == status.HTTP_200_OK

    listing.refresh_from_db()

    assert listing.is_active is True
    assert listing.deleted_at is None


def test_restore_listing_requires_owner(
    api_client,
    listing,
    user,
):
    """
    Check that another user cannot restore a listing.
    """
    from django.utils import timezone

    listing.is_active = False
    listing.deleted_at = timezone.now()
    listing.save(update_fields=["is_active", "deleted_at"])

    other_user = BookingUser.objects.create_user(
        email="restoreother@example.com",
        password="TestPassword1!",
        first_name="Other",
        last_name="User",
        phone="+496666666666",
    )

    api_client.force_authenticate(user=other_user)

    url = reverse(
        "listings-restore",
        kwargs={"pk": listing.id},
    )

    response = api_client.post(url)

    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_photo_list(api_client, listing, photo):
    """
    Check that photos can be listed.
    """
    api_client.force_authenticate(user=listing.owner)

    url = reverse("photo-list")

    response = api_client.get(
        url,
        {"listing": str(listing.id)},
    )

    assert response.status_code == status.HTTP_200_OK


def test_photo_retrieve(api_client, listing, photo):
    """
    Check that a photo can be retrieved.
    """
    api_client.force_authenticate(user=listing.owner)

    url = reverse(
        "photo-detail",
        kwargs={"pk": photo.id},
    )

    response = api_client.get(url)

    assert response.status_code == status.HTTP_200_OK
    assert response.data["id"] == str(photo.id)


def test_delete_photo_owner(api_client, listing, photo):
    """
    Check that the listing owner can delete a photo.
    """
    api_client.force_authenticate(user=listing.owner)

    url = reverse(
        "photo-detail",
        kwargs={"pk": photo.id},
    )

    response = api_client.delete(url)

    assert response.status_code == status.HTTP_204_NO_CONTENT


def test_delete_photo_other_user_forbidden(
    api_client,
    listing,
    photo,
):
    """
    Check that another user cannot delete a listing photo.
    """
    other_user = BookingUser.objects.create_user(
        email="photoother@example.com",
        password="TestPassword1!",
        first_name="Other",
        last_name="User",
        phone="+497777777777",
    )

    api_client.force_authenticate(user=other_user)

    url = reverse(
        "photo-detail",
        kwargs={"pk": photo.id},
    )

    response = api_client.delete(url)

    assert response.status_code == status.HTTP_403_FORBIDDEN