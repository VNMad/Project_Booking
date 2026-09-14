from rest_framework.routers import DefaultRouter

from .views import ListingViewSet, PhotoViewSet


router = DefaultRouter()

router.register("photos", PhotoViewSet, basename="photo")
router.register("", ListingViewSet, basename="listings")


urlpatterns = router.urls