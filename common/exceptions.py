from common.common_exceptions import CommonAPIException


class InvalidPathParameterException(CommonAPIException):
    status_code = 400
    default_detail = '입력값을 다시 확인해주세요.'
    default_code = 'invalid-path-parameter'


class ExternalAPIException(CommonAPIException):
    status_code = 500
    default_detail = '외부 API 통신 중 에러가 발생했습니다.'
    default_code = 'external-api-error'
