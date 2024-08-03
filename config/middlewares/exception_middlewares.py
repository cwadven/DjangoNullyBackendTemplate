from common.common_exceptions import CommonAPIException
from config.settings.base import logger
from rest_framework import exceptions
from rest_framework.views import exception_handler


def custom_exception_handler(exc, context):
    logger.error(f'{exc}, {context}')

    response = exception_handler(exc, context)

    if response is not None:
        message = ''
        error_code = 'unexpected-error'
        errors = None
        if isinstance(exc, exceptions.ParseError):
            message = exc.default_detail
            error_code = exc.default_code
        elif isinstance(exc, exceptions.AuthenticationFailed):
            message = exc.default_detail
            error_code = exc.default_code
        elif isinstance(exc, exceptions.NotAuthenticated):
            message = 'No Auth'
            error_code = exc.default_code
        elif isinstance(exc, exceptions.PermissionDenied):
            message = exc.default_detail
            error_code = exc.default_code
        elif isinstance(exc, exceptions.NotFound):
            message = exc.default_detail
            error_code = exc.default_code
        elif isinstance(exc, exceptions.MethodNotAllowed):
            message = exc.default_detail
            error_code = exc.default_code
        elif isinstance(exc, exceptions.NotAcceptable):
            message = exc.default_detail
            error_code = exc.default_code
        elif isinstance(exc, exceptions.UnsupportedMediaType):
            message = exc.default_detail
            error_code = exc.default_code
        elif isinstance(exc, exceptions.Throttled):
            message = exc.default_detail
            error_code = exc.default_code
        elif isinstance(exc, exceptions.ValidationError):
            message = exc.default_detail
            error_code = exc.default_code
        elif isinstance(exc, CommonAPIException):
            message = exc.default_detail
            error_code = exc.default_code
            errors = exc.errors
        elif isinstance(exc, exceptions.APIException):
            message = exc.default_detail
            error_code = exc.default_code
            errors = None

        response.data['message'] = message
        response.data['error_code'] = error_code
        response.data['errors'] = errors
        response.data.pop('detail', None)
        return response
    else:
        return response
