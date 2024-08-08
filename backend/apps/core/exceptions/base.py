from typing import TypedDict, List

from rest_framework import status
from rest_framework.exceptions import APIException
from django.utils.translation import gettext_lazy as _
from rest_framework.status import HTTP_400_BAD_REQUEST


class FieldError(TypedDict):
    field: str
    message: str


def serializer_errors_to_field_errors(serializer_errors) -> List[FieldError]:
    field_errors = []
    for field, messages in serializer_errors.items():
        for message in messages:
            field_errors.append(FieldError(
                field=field,
                message=_(message)
            ))
    return field_errors


class DetailExceptionDict(TypedDict):
    message: str
    fields_errors: List[FieldError]


class CoreExceptions:
    class SomethingGoWrong(APIException):
        status_code = status.HTTP_400_BAD_REQUEST
        default_detail = {'message': _('Sorry, something went wrong. We are already working to resolve the problem.')}
        default_code = 'username_already_exists'

    class WrongFilledFields(APIException):
        status_code = status.HTTP_400_BAD_REQUEST
        default_detail = {'message': _('Correct the mistakes.')}
        default_code = 'wrong_filled_fields'

    class AccessDenied(APIException):
        status_code = status.HTTP_403_FORBIDDEN
        default_detail = {'message': _('Access denied.')}
        default_code = 'access_denied'

    class CaptchaInvalid(APIException):
        status_code = status.HTTP_403_FORBIDDEN
        default_detail = {'message': _('Looks like there was a captcha error. Please try again.')}
        default_code = 'Captcha Invalid'

    class DetailAPIException(APIException):
        status_code = status.HTTP_400_BAD_REQUEST

        def __init__(self, detail: DetailExceptionDict, code: str = None, status_code: str = None):
            if status_code is not None:
                self.status_code = status_code
            super().__init__(detail=detail, code=code or 'error')

    class SerializerErrors(DetailAPIException):
        def __init__(self, serializer_errors: dict, code: str = None, status_code: str = HTTP_400_BAD_REQUEST,
                     message: str = _('Correct the mistakes.')):
            detail = DetailExceptionDict(
                message=message,
                fields_errors=serializer_errors_to_field_errors(serializer_errors)
            )
            super().__init__(detail=detail, code=code, status_code=status_code)
