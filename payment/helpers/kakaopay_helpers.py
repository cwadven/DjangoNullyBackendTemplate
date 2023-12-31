import requests
from abc import ABC
from django.conf import settings
from typing import Optional

from django.urls import reverse

from payment.exceptions import (
    KakaoPayCancelError,
    KakaoPaySuccessError,
)


class KakaoPay:
    def __init__(self, handler: 'KakaoPayHandler') -> None:
        self.kakao_pay_api_key = settings.KAKAO_PAY_API_KEY
        self.kakao_pay_ready_url = 'https://kapi.kakao.com/v1/payment/ready'
        self.kakao_pay_approve_url = 'https://kapi.kakao.com/v1/payment/approve'
        self.kakao_pay_cancel_url = 'https://kapi.kakao.com/v1/payment/cancel'
        self.headers = {
            'Authorization': 'KakaoAK ' + self.kakao_pay_api_key,
            'Content-type': 'application/x-www-form-urlencoded;charset=utf-8',
        }
        self.handler = handler

    def ready_to_pay(
            self,
            order_id: str,
            guest_id: str,
            product_name: str,
            quantity: str,
            total_amount: str,
            tax_free_amount: str
    ) -> dict:
        """
        아래와 같은 형태로 return
        {
            "tid": "T469b847306d7b2dc394",
            "tms_result": false,
            "next_redirect_app_url": "https://online-pay.kakao.com/mockup/v1/1d61e5d04016bd94c9ed54406bb51f1194e3772ce297a097fdb3e3604fc42e46/aInfo",
            "next_redirect_mobile_url": "https://online-pay.kakao.com/mockup/v1/1d61e5d04016bd94c9ed54406bb51f1194e3772ce297a097fdb3e3604fc42e46/mInfo",
            "next_redirect_pc_url": "https://online-pay.kakao.com/mockup/v1/1d61e5d04016bd94c9ed54406bb51f1194e3772ce297a097fdb3e3604fc42e46/info",
            "android_app_scheme": "kakaotalk://kakaopay/pg?url=https://online-pay.kakao.com/pay/mockup/1d61e5d04016bd94c9ed54406bb51f1194e3772ce297a097fdb3e3604fc42e46",
            "ios_app_scheme": "kakaotalk://kakaopay/pg?url=https://online-pay.kakao.com/pay/mockup/1d61e5d04016bd94c9ed54406bb51f1194e3772ce297a097fdb3e3604fc42e46",
            "created_at": "2023-05-21T15:20:55"
        }
        """
        params = {
            'cid': settings.KAKAO_PAY_CID,
            'partner_order_id': order_id,
            'partner_user_id': guest_id,
            'item_name': product_name,
            'quantity': '1',
            'total_amount': total_amount,
            'tax_free_amount': tax_free_amount,
            'approval_url': self.handler.approval_url,
            'cancel_url': self.handler.cancel_url,
            'fail_url': self.handler.fail_url,
        }
        res = requests.post(self.kakao_pay_ready_url, headers=self.headers, params=params)
        return res.json()

    def approve_payment(self, tid: str, pg_token: str, order_id: str, guest_id: str) -> dict:
        """
        https://developers.kakao.com/docs/latest/ko/kakaopay/single-payment

        아래와 같은 형태로 return
        {
            "aid": "A469b85a306d7b2dc395",
            "tid": "T469b847306d7b2dc394",
            "cid": "TC0ONETIME",
            "partner_order_id": "test1",
            "partner_user_id": "1",
            "payment_method_type": "MONEY",
            "item_name": "1000 포인트",
            "item_code": "",
            "quantity": 1,
            "amount": {
                "total": 1000,
                "tax_free": 0,
                "vat": 91,
                "point": 0,
                "discount": 0,
                "green_deposit": 0
            },
            "created_at": "2023-05-21T15:20:55",
            "approved_at": "2023-05-21T15:25:31"
        }
        """
        params = {
            'cid': settings.KAKAO_PAY_CID,
            'tid': tid,
            'partner_order_id': order_id,
            'partner_user_id': guest_id,
            'pg_token': pg_token,
        }
        res = requests.post(self.kakao_pay_approve_url, headers=self.headers, params=params)
        response = res.json()
        if res.status_code == 400:
            extras = response.get('extras')
            if extras:
                raise KakaoPaySuccessError(extras['method_result_message'])
        if res.status_code != 200:
            raise KakaoPaySuccessError()
        return response

    def cancel_payment(self, tid: str, cancel_price: int, cancel_tax_free_price: int, payload: str) -> dict:
        """
        https://developers.kakao.com/docs/latest/ko/kakaopay/cancellation

        payload는 200 글자 넘으면 안됨

        아래와 같은 형태로 return
        {
            "aid": "A5922f8a3ad74821a2cf",
            "tid": "T591a8da3ad748219fdf",
            "cid": "TC0ONETIME",
            "status": "CANCEL_PAYMENT",
            "partner_order_id": "6",
            "partner_user_id": "4",
            "payment_method_type": "MONEY",
            "item_name": "G-point 1000",
            "quantity": 10,
            "amount": {
                "total": 10000,
                "tax_free": 0,
                "vat": 909,
                "point": 0,
                "discount": 0,
                "green_deposit": 0
            },
            "approved_cancel_amount": {
                "total": 10000,
                "tax_free": 0,
                "vat": 909,
                "point": 0,
                "discount": 0,
                "green_deposit": 0
            },
            "canceled_amount": {
                "total": 10000,
                "tax_free": 0,
                "vat": 909,
                "point": 0,
                "discount": 0,
                "green_deposit": 0
            },
            "cancel_available_amount": {
                "total": 0,
                "tax_free": 0,
                "vat": 0,
                "point": 0,
                "discount": 0,
                "green_deposit": 0
            },
            "created_at": "2024-01-01T02:46:03",
            "approved_at": "2024-01-01T02:46:34",
            "canceled_at": "2024-01-01T12:20:42",
            "payload": "테스"
        }
        """
        params = {
            'cid': settings.KAKAO_PAY_CID,
            'tid': tid,
            'cancel_amount': cancel_price,
            'cancel_tax_free_amount': cancel_tax_free_price,
            'payload': payload,
        }
        res = requests.post(self.kakao_pay_cancel_url, headers=self.headers, params=params)
        response = res.json()
        if res.status_code == 400:
            extras = response.get('extras')
            if extras:
                raise KakaoPayCancelError(extras['method_result_message'])
        if res.status_code != 200:
            raise KakaoPayCancelError()
        return res.json()


class KakaoPayHandler(ABC):
    approval_url: Optional[str] = None
    cancel_url: Optional[str] = None
    fail_url: Optional[str] = None


class KakaoPayProductHandler(KakaoPayHandler):
    def __init__(self, order_id: int):
        # 프론트엔드 개발자가 결제 성공/실패/취소 시 이동할 url을 결정하면 그 url을 넣어줘야 함
        # 혹은 프론트엔드 개발자가 결제 성공/실패/취소 시 이동할 url을 결정하지 않았다면
        # 결제 성공/실패/취소 시 이동할 html 을 따로 만들어서 url 결정해줘야 함
        self.approval_url = settings.BASE_DOMAIN + reverse('payment:product_approve', args=[order_id])
        self.cancel_url = settings.BASE_DOMAIN + reverse('payment:product_cancel', args=[order_id])
        self.fail_url = settings.BASE_DOMAIN + reverse('payment:product_fail', args=[order_id])
