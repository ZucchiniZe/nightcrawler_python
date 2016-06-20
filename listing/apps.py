from django.apps import AppConfig


class ListingConfig(AppConfig):
    name = 'listing'

    def ready(self):
        import listing.signals
