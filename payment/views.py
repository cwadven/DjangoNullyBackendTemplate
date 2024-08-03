from common.common_decorators.request_decorators import (
    mandatories,
    optionals,
)
from django.shortcuts import render
from payment.consts import (
    PAY_ABUSED_HTML_TEMPLATE,
    PAY_CANCEL_HTML_TEMPLATE,
    PAY_FAIL_HTML_TEMPLATE,
    PAY_SUCCESS_HTML_TEMPLATE,
)
from payment.dtos.request_dtos import KakaoPayReadyForBuyProductRequest
from payment.dtos.response_dtos import KakaoPayReadyForBuyProductResponse
from payment.exceptions import (
    KakaoPayCancelError,
    UnavailablePayHandler,
)
from payment.helpers.kakaopay_helpers import (
    KakaoPay,
    KakaoPayProductHandler,
)
from payment.services import (
    kakao_pay_approve_give_product_cancel,
    kakao_pay_approve_give_product_fail,
    kakao_pay_approve_give_product_success,
)
from product.exceptions import ProductNotExists
from product.models import (
    PointProduct,
)
from rest_framework.exceptions import APIException
from rest_framework.response import Response
from rest_framework.views import APIView


class KakaoPayReadyForBuyProductAPIView(APIView):
    @mandatories('product_id', 'product_type', 'quantity', 'payment_type', 'order_phone_number')
    def post(self, request, m):
        kakao_pay_ready_for_buy_product_request = KakaoPayReadyForBuyProductRequest(
            product_id=m['product_id'],
            product_type=m['product_type'],
            quantity=m['quantity'],
            payment_type=m['payment_type'],
            order_phone_number=m['order_phone_number'],
        )
        # 나중에 리팩토링 필요 Handler 로 원하는 Product 잡기
        if kakao_pay_ready_for_buy_product_request.product_type == PointProduct.product_type:
            try:
                product = PointProduct.objects.get_actives().get(
                    id=kakao_pay_ready_for_buy_product_request.product_id,
                )
            except PointProduct.DoesNotExist:
                raise ProductNotExists()
        else:
            raise UnavailablePayHandler()

        order = product.initialize_order(
            guest=request.guest,
            order_phone_number=kakao_pay_ready_for_buy_product_request.order_phone_number,
            payment_type=kakao_pay_ready_for_buy_product_request.payment_type,
            quantity=kakao_pay_ready_for_buy_product_request.quantity,
        )
        kakao_pay = KakaoPay(
            KakaoPayProductHandler(order_id=order.id)
        )
        product_name = product.title
        if kakao_pay_ready_for_buy_product_request.quantity > 1:
            product_name += f' ({kakao_pay_ready_for_buy_product_request.quantity}개)'
        ready_to_pay = kakao_pay.ready_to_pay(
            order_id=str(order.id),
            guest_id=str(request.guest.id),
            product_name=product_name,
            quantity='1',
            total_amount=order.total_paid_price,
            tax_free_amount=0,
        )
        order.tid = ready_to_pay['tid']
        order.save(update_fields=['tid'])
        return Response(
            KakaoPayReadyForBuyProductResponse(
                tid=ready_to_pay['tid'],
                next_redirect_app_url=ready_to_pay['next_redirect_app_url'],
                next_redirect_mobile_url=ready_to_pay['next_redirect_mobile_url'],
                next_redirect_pc_url=ready_to_pay['next_redirect_pc_url'],
            ).model_dump(),
            status=200
        )


class KakaoPayApproveForBuyProductAPIView(APIView):
    def get(self, request, order_id):
        pg_token = request.GET.get('pg_token')
        kakao_pay_approve_give_product_success(order_id, pg_token)
        return Response({'message': '결제가 완료되었습니다.'}, status=200)


class KakaoPayCancelForBuyProductAPIView(APIView):
    @optionals({'reason': '결제 취소'})
    def post(self, request, order_token, o):
        kakao_pay_approve_give_product_cancel(order_token, o['reason'])
        return Response({'message': '결제가 취소되었습니다.'}, status=200)


class KakaoPayFailForBuyProductAPIView(APIView):
    def post(self, request, order_token):
        kakao_pay_approve_give_product_fail(order_token)
        return Response({'message': '결제가 실패되었습니다.'}, status=200)


def approve_give_product_success_by_template(request, order_id):
    pg_token = request.GET.get('pg_token')
    try:
        kakao_pay_approve_give_product_success(order_id, pg_token)
    except APIException:
        return render(request, PAY_ABUSED_HTML_TEMPLATE)

    return render(request, PAY_SUCCESS_HTML_TEMPLATE)


@optionals({'reason': '결제 취소'})
def approve_give_product_cancel_by_template(request, order_token, o):
    try:
        kakao_pay_approve_give_product_cancel(order_token, o['reason'])
    except KakaoPayCancelError:
        return render(request, PAY_CANCEL_HTML_TEMPLATE)
    except APIException:
        return render(request, PAY_ABUSED_HTML_TEMPLATE)
    return render(request, PAY_CANCEL_HTML_TEMPLATE)


def approve_give_product_fail_by_template(request, order_token):
    try:
        kakao_pay_approve_give_product_fail(order_token)
    except APIException:
        return render(request, PAY_ABUSED_HTML_TEMPLATE)

    return render(request, PAY_FAIL_HTML_TEMPLATE)
