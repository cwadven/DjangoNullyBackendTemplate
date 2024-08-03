from django.urls import path
from payment.views import (
    KakaoPayApproveForBuyProductAPIView,
    KakaoPayCancelForBuyProductAPIView,
    KakaoPayFailForBuyProductAPIView,
    KakaoPayReadyForBuyProductAPIView,
    approve_give_product_cancel_by_template,
    approve_give_product_fail_by_template,
    approve_give_product_success_by_template,
)

app_name = 'payment'


urlpatterns = [
    path('product/buy/kakao', KakaoPayReadyForBuyProductAPIView.as_view(), name='product_buy'),
    path('product/approve/kakao/<int:order_id>', KakaoPayApproveForBuyProductAPIView.as_view(), name='product_approve'),
    path('product/cancel/kakao/<str:order_token>', KakaoPayCancelForBuyProductAPIView.as_view(), name='product_cancel'),
    path('product/fail/kakao/<str:order_token>', KakaoPayFailForBuyProductAPIView.as_view(), name='product_fail'),

    path('product/approve/kakao/template/<int:order_id>', approve_give_product_success_by_template, name='product_approve_template'),
    path('product/cancel/kakao/template/<str:order_token>', approve_give_product_cancel_by_template, name='product_cancel_template'),
    path('product/fail/kakao/template/<str:order_token>', approve_give_product_fail_by_template, name='product_fail_template'),
]
