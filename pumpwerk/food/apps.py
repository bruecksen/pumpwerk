from django.apps import AppConfig


class FoodConfig(AppConfig):
    name = 'pumpwerk.food'

    def ready(self):
        import pumpwerk.food.signals  # noqa