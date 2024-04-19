from django.apps import AppConfig
import logging
from django.db.models.signals import post_migrate


class ApiConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'api'

    def ready(self) -> None:
        from . import signals
        post_migrate.connect(self.check_initalize_point)

    def check_initalize_point(self, **kwargs):
        from .models import Point
        from .utils.timeUtils import get_datetime_now

        logger = logging.getLogger(__name__)
        if not Point.objects.exists():
            default_point = Point.objects.create()
            default_point.save()
            logger.info('{}: Initialize default point'.format(
                get_datetime_now()))
