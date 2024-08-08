import logging
import random

from django.db import connections
from django_minio_backend import MinioBackend
from django_redis import get_redis_connection
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from apps.core.tasks.test_tasks import test_task
from utils.djrediser import DjRediser

log = logging.getLogger('console')


@api_view(('GET',))
def health_test(request) -> Response:
    test_task.delay(random.randint(1000, 10000))
    # Check Redis
    if not get_redis_connection().flushall():
        log.error('Redis have not yet come to life')
        return Response('Redis error', status=status.HTTP_503_SERVICE_UNAVAILABLE)

    print(DjRediser().cache('health_test_cache', lambda: random.randint(1000, 10000)))

    try:
        connections['default'].cursor()
    except Exception as e:
        log.error(f'DB have not yet come to life: {str(e)}')
        return Response(f'DB error: {str(e)}', status=status.HTTP_503_SERVICE_UNAVAILABLE)

    # Check Minio
    minio_available = MinioBackend().is_minio_available()  # An empty string is fine this time
    if not minio_available:
        log.error(f'MINIO ERROR')
        log.error(minio_available.details)
        log.error(f'MINIO_STATIC_FILES_BUCKET = {MinioBackend().MINIO_STATIC_FILES_BUCKET}')
        log.error(f'MINIO_MEDIA_FILES_BUCKET = {MinioBackend().MINIO_MEDIA_FILES_BUCKET}')
        log.error(f'base_url = {MinioBackend().base_url}')
        log.error(f'base_url_external = {MinioBackend().base_url_external}')
        log.error(f'HTTP_CLIENT = {MinioBackend().HTTP_CLIENT}')
        return Response('MINIO ERROR', status=status.HTTP_503_SERVICE_UNAVAILABLE)
    return Response('OK')
