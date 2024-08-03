from django.urls import path
from product.views import PointProductListAPIView

app_name = 'product'


urlpatterns = [
    path('point', PointProductListAPIView.as_view(), name='points'),
]
