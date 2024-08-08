# core/user.py

from django.contrib.auth.models import AbstractUser
from django.db.models import CharField, DateField, BooleanField, ImageField
from django.utils.translation import gettext_lazy as _


class User(AbstractUser):
    phone = CharField(_('Phone'), max_length=64, blank=True, null=True)
    middle_name = CharField(_('Middle name'), max_length=150, blank=True)
    birth_date = DateField(_('Birth date'), null=True, blank=True)
    avatar = ImageField(_('Avatar'), upload_to='user/images/avatar/', null=True, blank=True)
    is_test = BooleanField(_('Is test'), default=False)
