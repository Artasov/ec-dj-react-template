import asyncio
import functools
import hashlib
import hmac
import json
import logging
import os
import time
import urllib
import urllib.parse
import urllib.request
from datetime import timedelta, datetime
from time import time

import aiohttp
from django.conf import settings
from django.contrib.auth.models import Group
from django.core.handlers.asgi import ASGIRequest
from django.core.handlers.wsgi import WSGIRequest
from django.db import transaction
from django.http import HttpResponseNotAllowed, HttpResponse
from django.shortcuts import redirect
from django.utils.timezone import now
from rest_framework import status
from rest_framework.response import Response

log = logging.getLogger('base')


def add_user_to_group(user, group_name):
    group, created = Group.objects.get_or_create(name=group_name)
    if user not in group.user_set.all():
        group.user_set.add(user)


def get_timedelta(**kwargs) -> datetime:
    return now() + timedelta(**kwargs)


def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def google_captcha_validation(request):
    recaptcha_response = request.POST.get('g-recaptcha-response')
    url = 'https://www.google.com/recaptcha/api/siteverify'
    values = {
        'secret': settings.GOOGLE_RECAPTCHA_SECRET_KEY,
        'response': recaptcha_response
    }
    data = urllib.parse.urlencode(values).encode()
    req = urllib.request.Request(url, data=data)
    response = urllib.request.urlopen(req)
    result = json.loads(response.read().decode())
    return result


def decrease_by_percentage(num: int, percent: int) -> int:
    return round(num * (1 - percent / 100))


def get_plural_form_number(number: int, forms: tuple):
    """get_plural_form_number(minutes, ('минуту', 'минуты', 'минут'))"""
    if number % 10 == 1 and number % 100 != 11:
        return forms[0]
    elif 2 <= number % 10 <= 4 and (number % 100 < 10 or number % 100 >= 20):
        return forms[1]
    else:
        return forms[2]


# async def get_user_by_email_or_name(identifier: str) -> Tuple[Optional[User], str]:
#     """Retrieve User by email or username. Returns User and empty string or None and error message."""
#     try:
#         lookup_field = 'email' if '@' in identifier else 'username'
#         return await User.objects.aget(**{lookup_field: identifier}), ''
#     except User.DoesNotExist:
#         return None, USER_EMAIL_NOT_EXISTS if '@' in identifier else USER_USERNAME_NOT_EXISTS


def telegram_verify_hash(auth_data):
    check_hash = auth_data['hash']

    del auth_data['hash']
    data_check_arr = []
    for key, value in auth_data.items():
        data_check_arr.append(f'{key}={value}')
    data_check_arr.sort()
    data_check_string = '\n'.join(data_check_arr)
    secret_key = hashlib.sha256(os.getenv('TELEGRAM_TOKEN').encode()).digest()
    hash = hmac.new(secret_key, data_check_string.encode(), hashlib.sha256).hexdigest()
    if hash != check_hash:
        return False
    if time.time() - int(auth_data['auth_date']) > 86400:
        return False
    return True


async def check_recaptcha_is_valid(recaptcha_response: str) -> bool:
    if not recaptcha_response:
        return False

    url = 'https://www.google.com/recaptcha/api/siteverify'
    values = {
        'secret': settings.GOOGLE_RECAPTCHA_SECRET_KEY,
        'response': recaptcha_response
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(url, data=values) as response:
            if response.status == 200:
                result = await response.json()
                return result.get('success', False)
            return False


def allowed_only(allowed_methods):
    def decorator(view_func):
        def wrapped_view(request, *args, **kwargs):
            if request.method in allowed_methods:
                return view_func(request, *args, **kwargs)
            else:
                return HttpResponseNotAllowed(allowed_methods)

        return wrapped_view

    return decorator


def aallowed_only_async(allowed_methods) -> callable:
    def decorator(view_func) -> callable:
        async def wrapped_view(request, *args, **kwargs) -> HttpResponse:
            if request.method in allowed_methods:
                if asyncio.iscoroutinefunction(view_func):
                    return await view_func(request, *args, **kwargs)
                else:
                    return view_func(request, *args, **kwargs)
            else:
                return HttpResponseNotAllowed(allowed_methods)

        return wrapped_view

    return decorator


def forbidden_with_login(fn) -> callable:
    @functools.wraps(fn)
    def inner(request, *args, **kwargs):
        if request.user.is_authenticated:
            return Response(status=status.HTTP_403_FORBIDDEN)
        else:
            return fn(request, *args, **kwargs)

    return inner


def aforbidden_with_login(fn) -> callable:
    @functools.wraps(fn)
    async def inner(request, *args, **kwargs) -> Response:
        if request.user.is_authenticated:
            return Response(status=status.HTTP_403_FORBIDDEN)
        else:
            return await fn(request, *args, **kwargs)

    return inner


def acontroller(name=None, log_time=False, auth=False) -> callable:
    def decorator(fn) -> callable:
        @functools.wraps(fn)
        async def inner(request: ASGIRequest, *args, **kwargs):
            fn_name = name or fn.__name__
            if settings.DEBUG:
                print(f'AController: {request.method} | {fn_name}')
            else:
                log.info(f'AController: {request.method} | {fn_name}')
            if log_time:
                start_time = time()

            # if auth:
            #     user = await sync_to_async(lambda: request.user)()
            #     print(user)
            #     is_authenticated = await sync_to_async(lambda: request.user.is_authenticated)()
            #     print('0-0')
            #     print(is_authenticated)
            #     if not is_authenticated:
            #         return redirect(settings.LOGIN_URL)

            if settings.DEBUG:
                return await fn(request, *args, **kwargs)
            else:
                try:
                    if log_time:
                        end_time = time()
                        elapsed_time = end_time - start_time
                        log.info(f"Execution time of {fn_name}: {elapsed_time:.2f} seconds")
                    return await fn(request, *args, **kwargs)
                except Exception as e:
                    log.critical(f"ERROR in {fn_name}: {str(e)}", exc_info=True)
                    # send_text_email(
                    #     subject='SERVER ERROR',
                    #     to_email=settings.DEVELOPER_EMAIL,
                    #     text=f"error_message: {str(e)}\n"
                    #          f"traceback:\n{traceback.format_exc()}"
                    # )
                    raise e

        return inner

    return decorator


def controller(name=None, log_time=False, auth=False) -> callable:
    def decorator(fn) -> callable:
        @functools.wraps(fn)
        def inner(request: WSGIRequest, *args, **kwargs):
            fn_name = name or fn.__name__
            log.info(f'Sync Controller: {request.method} | {fn_name}')
            if log_time:
                start_time = time()
            if auth:
                if not request.user.is_authenticated:
                    return redirect(settings.LOGIN_URL)
            if settings.DEBUG:
                with transaction.atomic():
                    return fn(request, *args, **kwargs)
            else:
                try:
                    if log_time:
                        end_time = time()
                        elapsed_time = end_time - start_time
                        log.info(f"Execution time of {fn_name}: {elapsed_time:.2f} seconds")
                    with transaction.atomic():
                        return fn(request, *args, **kwargs)
                except Exception as e:
                    log.critical(f"ERROR in {fn_name}: {str(e)}", exc_info=True)
                    # send_text_email(
                    #     subject='Ошибка на сервере',
                    #     to_email=settings.DEVELOPER_EMAIL,
                    #     text=f"error_message: {str(e)}\n"
                    #          f"traceback:\n{traceback.format_exc()}"
                    # )
                    raise e

        return inner

    return decorator
