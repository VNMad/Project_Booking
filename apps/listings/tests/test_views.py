from datetime import timedelta
from io import BytesIO
from PIL import Image
from core.constants import LISTING_MAX_PHOTOS

from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from django.utils import timezone
from rest_framework import status

from apps.bookings.services import create_booking
from apps.listings.models import Listing, Photo
from apps.users.models import BookingUser


def get_future_booking_dates():
    """
    Return future check-in and check-out dates for booking tests.
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


def create_uploaded_image(name="test.png"):
    """
    Create a valid image file for photo API tests.
    """
    image = Image.new("RGB", (10, 10))

    buffer = BytesIO()
    image.save(buffer, format="PNG")

    return SimpleUploadedFile(
        name=name,
        content=buffer.getvalue(),
        content_type="image/png",
    )


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


def test_delete_listing_with_active_booking_is_rejected(
    api_client,
    user,
    booking_owner,
    booking_listing,
):
    """
    Check that a listing with an active booking cannot be deleted.
    """
    date_start, date_end = get_future_booking_dates()

    create_booking(
        tenant=user,
        listing_id=booking_listing.id,
        date_start=date_start,
        date_end=date_end,
    )

    api_client.force_authenticate(user=booking_owner)

    url = reverse(
        "listings-detail",
        kwargs={"pk": booking_listing.id},
    )

    response = api_client.delete(url)

    assert response.status_code == status.HTTP_400_BAD_REQUEST

    booking_listing.refresh_from_db()

    assert booking_listing.is_active is True
    assert booking_listing.deleted_at is None


def test_delete_already_deleted_listing_is_rejected(
    api_client,
    listing,
):
    """
    Check that an already soft-deleted listing cannot be deleted again.
    """
    listing.is_active = False
    listing.deleted_at = timezone.now()
    listing.save(update_fields=["is_active", "deleted_at"])

    api_client.force_authenticate(user=listing.owner)

    url = reverse(
        "listings-detail",
        kwargs={"pk": listing.id},
    )

    response = api_client.delete(url)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.data["detail"] == "Listing is already deleted."


def test_restore_active_listing_is_rejected(
    api_client,
    listing,
):
    """
    Check that an active listing cannot be restored.
    """
    api_client.force_authenticate(user=listing.owner)

    url = reverse(
        "listings-restore",
        kwargs={"pk": listing.id},
    )

    response = api_client.post(url)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.data["detail"] == "This listing is not deleted."


def test_patch_deleted_listing_is_rejected(
    api_client,
    listing,
):
    """
    Check that a soft-deleted listing cannot be partially updated.
    """
    listing.is_active = False
    listing.deleted_at = timezone.now()
    listing.save(update_fields=["is_active", "deleted_at"])

    api_client.force_authenticate(user=listing.owner)

    url = reverse(
        "listings-detail",
        kwargs={"pk": listing.id},
    )

    response = api_client.patch(
        url,
        {"title": "Changed title"},
        format="json",
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST

    listing.refresh_from_db()

    assert listing.title == "Nice apartment in Berlin"


def test_put_deleted_listing_is_rejected(
    api_client,
    listing,
):
    """
    Check that a soft-deleted listing cannot be fully updated.
    """
    listing.is_active = False
    listing.deleted_at = timezone.now()
    listing.save(update_fields=["is_active", "deleted_at"])

    api_client.force_authenticate(user=listing.owner)

    url = reverse(
        "listings-detail",
        kwargs={"pk": listing.id},
    )

    response = api_client.put(
        url,
        {"title": "Changed title"},
        format="json",
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST

    listing.refresh_from_db()

    assert listing.title == "Nice apartment in Berlin"


def test_listing_owner_can_create_photo(
    api_client,
    listing,
    tmp_path,
    settings,
):
    """
    Check that the listing owner can add a photo.
    """
    settings.MEDIA_ROOT = tmp_path

    api_client.force_authenticate(user=listing.owner)

    url = reverse("photo-list")

    data = {
        "listing": str(listing.id),
        "image": create_uploaded_image(),
        "position": 1,
    }

    response = api_client.post(
        url,
        data,
        format="multipart",
    )

    assert response.status_code == status.HTTP_201_CREATED
    assert Photo.objects.filter(listing=listing).count() == 1


def test_other_user_cannot_create_photo(
    api_client,
    listing,
    booking_owner,
    tmp_path,
    settings,
):
    """
    Check that another user cannot add a photo
    to someone else's listing.
    """
    settings.MEDIA_ROOT = tmp_path

    api_client.force_authenticate(user=booking_owner)

    url = reverse("photo-list")

    data = {
        "listing": str(listing.id),
        "image": create_uploaded_image(),
        "position": 1,
    }

    response = api_client.post(
        url,
        data,
        format="multipart",
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert Photo.objects.filter(listing=listing).count() == 0


def test_listing_photo_limit_is_enforced(
    api_client,
    listing,
    tmp_path,
    settings,
):
    """
    Check that a listing cannot contain more
    than the configured maximum number of photos.
    """
    settings.MEDIA_ROOT = tmp_path

    for position in range(1, LISTING_MAX_PHOTOS + 1):
        Photo.objects.create(
            listing=listing,
            image=create_uploaded_image(
                name=f"photo_{position}.png",
            ),
            position=position,
        )

    api_client.force_authenticate(user=listing.owner)

    url = reverse("photo-list")

    data = {
        "listing": str(listing.id),
        "image": create_uploaded_image(name="extra.png"),
        "position": LISTING_MAX_PHOTOS + 1,
    }

    response = api_client.post(
        url,
        data,
        format="multipart",
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert Photo.objects.filter(listing=listing).count() == LISTING_MAX_PHOTOS