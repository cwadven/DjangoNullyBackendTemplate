from django.urls import path
from promotion.views import PromotionBannerAPIView

app_name = 'promotion'


urlpatterns = [
    path('banners', PromotionBannerAPIView.as_view(), name='banners'),
]
