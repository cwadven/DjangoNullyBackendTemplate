from common.common_consts.common_enums import StrValueLabel


class ErrorMessage(StrValueLabel):
    INVALID_INPUT_ERROR_MESSAGE = ('invalid_input', '입력값을 다시 한번 확인해주세요.')
    INVALID_INPUT_DEPENDENCIES_ERROR = ('invalid_dependencies', '{}')
    INVALID_COMPARE_ERROR_NEED_TO_BE_BIGGER = ('invalid_compare_bigger', '{} 값은 {} 보다 커야합니다.')
    INVALID_COMPARE_ERROR_NEED_TO_BE_SMALLER = ('invalid_compare_smaller', '{} 값은 {} 보다 작아야합니다.')
    INVALID_MAXIMUM_LENGTH = ('invalid_maximum_length', '최대값을 초과했습니다.')
    INVALID_MINIMUM_ITEM_SIZE = ('invalid_minimum_item_size', '최소 {} 개가 필요합니다.')


class InvalidInputResponseErrorStatus(StrValueLabel):
    INVALID_INPUT_HOME_LIST_PARAM_ERROR_400 = (
        '400-invalid_home_list_input_error-00001', ErrorMessage.INVALID_INPUT_ERROR_MESSAGE.label
    )
    INVALID_PROJECT_CREATION_INPUT_DATA_ERROR_400 = (
        '400-project_creation-00001', ErrorMessage.INVALID_INPUT_ERROR_MESSAGE.label
    )
    INVALID_SIGN_UP_INPUT_DATA_400 = (
        '400-invalid_sign_up_input_data-00001', ErrorMessage.INVALID_INPUT_ERROR_MESSAGE.label
    )
    INVALID_PRE_SIGNED_URL_INPUT_DATA_400 = (
        '400-pre_signed_url_input_data-00001', ErrorMessage.INVALID_INPUT_ERROR_MESSAGE.label
    )
    INVALID_RECRUIT_JOB_INPUT_ERROR_400 = (
        '400-invalid_recruit_job_input-00001', ErrorMessage.INVALID_INPUT_ERROR_MESSAGE.label
    )
