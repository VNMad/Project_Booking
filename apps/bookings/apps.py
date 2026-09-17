from django.apps import AppConfig


class BookingsConfig(AppConfig):
    """  Configuration for the bookings application. """

    name = "apps.bookings"

    def ready(self):
        """
        Import booking signals when the application is ready.
        Importing the signals module registers all signal handlers with Django.
        """
        import apps.bookings.signals