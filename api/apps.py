from django.apps import AppConfig
import logging


class ApiConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'api'

    def ready(self) -> None:
        from . import signals
        self.check_initalize_point()

    def check_initalize_point(self):
        from .models import Point
        from .utils.timeUtils import get_datetime_now

        logger = logging.getLogger(__name__)
        if not Point.objects.exists():
            default_point = Point.objects.create()
            default_point.save()
            logger.info('{}: Initialize default point'.format(
                get_datetime_now()))
