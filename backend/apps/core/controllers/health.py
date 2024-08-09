import logging
from random import randint

from django.conf import settings
from django.db import connections
from django_minio_backend import MinioBackend
from django_redis import get_redis_connection
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.status import HTTP_503_SERVICE_UNAVAILABLE

from apps.core.tasks.test_tasks import test_task
from utils.djrediser import DjRediser

log = logging.getLogger('console')


@api_view(('GET',))
def health_test(request) -> Response:
    # Redis
    if not get_redis_connection():
        return Response('Redis is dead', HTTP_503_SERVICE_UNAVAILABLE)

    # Task
    test_task.delay(randint(1000, 10000))

    # Cache
    print(f"Cache health = {DjRediser.cache('health_test_cache', randint(1000, 10000))}")

    # Database
    try:
        connections['default'].cursor()
    except Exception as e:
        log.error(f'DB have not yet come to life: {str(e)}')
        return Response(f'Database is dead: {str(e)}', HTTP_503_SERVICE_UNAVAILABLE)

    # Minio
    if settings.MINIO_USE:
        MB = MinioBackend()
        if not MB.is_minio_available():
            log.error(f'Minio is dead')
            log.error(MB.is_minio_available().details)
            log.error(f'MINIO_STATIC_FILES_BUCKET = {MB.MINIO_STATIC_FILES_BUCKET}')
            log.error(f'MINIO_MEDIA_FILES_BUCKET = {MB.MINIO_MEDIA_FILES_BUCKET}')
            log.error(f'base_url = {MB.base_url}')
            log.error(f'base_url_external = {MB.base_url_external}')
            log.error(f'HTTP_CLIENT = {MB.HTTP_CLIENT}')
            return Response('Minio is dead', HTTP_503_SERVICE_UNAVAILABLE)
    return Response('ok')
