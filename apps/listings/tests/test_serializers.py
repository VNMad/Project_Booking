from apps.listings.serializers import ListingSerializer, PhotoSerializer


def test_listing_serializer_returns_listing_data(listing):
    """
    Check that ListingSerializer returns the expected listing data.
    """
    serializer = ListingSerializer(listing)

    assert serializer.data["id"] == str(listing.id)
    assert serializer.data["title"] == listing.title
    assert serializer.data["description"] == listing.description
    assert serializer.data["country"] == listing.country
    assert serializer.data["city"] == listing.city
    assert serializer.data["district"] == listing.district
    assert serializer.data["street"] == listing.street
    assert serializer.data["house_number"] == listing.house_number
    assert serializer.data["apartment_number"] == listing.apartment_number
    assert serializer.data["rooms"] == listing.rooms
    assert serializer.data["is_active"] is True


def test_listing_serializer_contains_photo_data(listing, photo):
    """
    Check that ListingSerializer includes listing photos.
    """
    serializer = ListingSerializer(listing)

    assert len(serializer.data["photos"]) == 1
    assert serializer.data["photos"][0]["position"] == 1


def test_listing_serializer_returns_review_statistics(listing):
    """
    Check that ListingSerializer returns review statistics fields.
    """
    serializer = ListingSerializer(listing)

    assert "reviews_count" in serializer.data
    assert "average_cleanliness" in serializer.data
    assert "average_location" in serializer.data


def test_listing_serializer_validates_maximum_photo_count(listing):
    """
    Check that ListingSerializer rejects more than the allowed
    number of photos.
    """
    data = {
        "title": listing.title,
        "description": listing.description,
        "country": listing.country,
        "city": listing.city,
        "district": listing.district,
        "street": listing.street,
        "house_number": listing.house_number,
        "apartment_number": "999",
        "price_per_night": "100.00",
        "rooms": listing.rooms,
        "photos": [
            {"position": position}
            for position in range(1, 12)
        ],
    }

    serializer = ListingSerializer(
        listing,
        data=data,
        partial=True,
    )

    assert serializer.is_valid() is False
    assert "photos" in serializer.errors


def test_photo_serializer_returns_photo_data(photo):
    """
    Check that PhotoSerializer returns the expected photo data.
    """
    serializer = PhotoSerializer(photo)

    assert serializer.data["id"] == str(photo.id)
    assert serializer.data["listing"] == str(photo.listing_id)
    assert serializer.data["position"] == 1


def test_photo_serializer_read_only_fields(photo):
    """
    Check that protected photo fields are read-only.
    """
    serializer = PhotoSerializer(photo)

    assert serializer.fields["id"].read_only is True
    assert serializer.fields["created_at"].read_only is True