from common.dtos.helper_dtos import (
    ConstanceDetailType,
    ConstanceType,
)


class ConstanceTypeHelper(object):
    def get_constance_types(self) -> list[ConstanceType]:
        raise NotImplementedError


CONSTANCE_TYPE_HELPER_MAPPER = {}


class ConstanceDetailTypeHelper(object):
    def get_constance_detail_types(self) -> list[ConstanceDetailType]:
        raise NotImplementedError
