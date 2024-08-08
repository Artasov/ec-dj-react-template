from django.utils.translation import gettext_lazy as _
from rest_framework import status
from rest_framework.response import Response

USER_CREATED_CONFIRM_EMAIL = _('The user has been created. Please check your email to confirm.')

SUCCESS_RENAME_CURRENT_USER = _('Great! You have successfully changed your username.')


class Responses:
    class Success:
        RenameCurrentUser = Response({'message': SUCCESS_RENAME_CURRENT_USER}, status=status.HTTP_200_OK)
