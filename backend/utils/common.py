# utils/common.py
from django.conf import settings
from django.urls import reverse


def build_full_url(pattern_name, *args, **kwargs):
    relative_url = reverse(pattern_name, args=args, kwargs=kwargs)
    full_url = f"{settings.DOMAIN_URL.rstrip('/')}{relative_url}"
    return full_url
