import uuid

from apps.statistic.serializers import ListingRatingSerializer, ListingStatisticsSerializer


def test_listing_rating_serializer_returns_expected_data():
    """
    Check that ListingRatingSerializer returns public listing statistics.
    """
    listing_id = uuid.uuid4()

    data = {
        "listing_id": listing_id,
        "reviews_count": 3,
        "average_cleanliness": 4.5,
        "average_location": 4.0,
    }

    serializer = ListingRatingSerializer(data)

    assert serializer.data["listing_id"] == str(listing_id)
    assert serializer.data["reviews_count"] == 3
    assert serializer.data["average_cleanliness"] == 4.5
    assert serializer.data["average_location"] == 4.0


def test_listing_rating_serializer_allows_null_averages():
    """
    Check that average ratings can be null when a listing has no reviews.
    """
    listing_id = uuid.uuid4()

    data = {
        "listing_id": listing_id,
        "reviews_count": 0,
        "average_cleanliness": None,
        "average_location": None,
    }

    serializer = ListingRatingSerializer(data)

    assert serializer.data["reviews_count"] == 0
    assert serializer.data["average_cleanliness"] is None
    assert serializer.data["average_location"] is None


def test_listing_statistics_serializer_returns_expected_data():
    """
    Check that ListingStatisticsSerializer returns extended statistics.
    """
    listing_id = uuid.uuid4()

    data = {
        "listing_id": listing_id,
        "reviews_count": 4,
        "average_cleanliness": 4.25,
        "average_location": 4.75,
        "bookings_count": 10,
        "confirmed_bookings": 3,
        "completed_bookings": 5,
    }

    serializer = ListingStatisticsSerializer(data)

    assert serializer.data["listing_id"] == str(listing_id)
    assert serializer.data["reviews_count"] == 4
    assert serializer.data["average_cleanliness"] == 4.25
    assert serializer.data["average_location"] == 4.75
    assert serializer.data["bookings_count"] == 10
    assert serializer.data["confirmed_bookings"] == 3
    assert serializer.data["completed_bookings"] == 5


def test_listing_statistics_serializer_inherits_rating_fields():
    """
    Check that extended statistics include all public rating fields.
    """
    serializer = ListingStatisticsSerializer()

    assert "listing_id" in serializer.fields
    assert "reviews_count" in serializer.fields
    assert "average_cleanliness" in serializer.fields
    assert "average_location" in serializer.fields

    assert "bookings_count" in serializer.fields
    assert "confirmed_bookings" in serializer.fields
    assert "completed_bookings" in serializer.fields