from rest_framework.routers import DefaultRouter

from .views import ListingStatisticsViewSet


router = DefaultRouter()

router.register("listings", ListingStatisticsViewSet, basename="listing-statistics")

urlpatterns = router.urls