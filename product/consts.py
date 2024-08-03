from common.common_consts.common_enums import StrValueLabel


class ProductGivenStatus(StrValueLabel):
    READY = ('READY', '지급 준비중')
    SUCCESS = ('SUCCESS', '지급 완료')
    FAIL = ('FAIL', '지급 실패')
    CANCEL = ('CANCEL', '지급 취소')


class ProductType(StrValueLabel):
    POINT = ('POINT', '포인트')
