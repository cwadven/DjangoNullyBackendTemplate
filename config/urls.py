from django.conf import settings
from django.contrib import admin
from django.urls import (
    include,
    path,
)
from django.views.generic import TemplateView


urlpatterns = [
    path('', TemplateView.as_view(template_name="homepage.html")),

    path('admin/', admin.site.urls),

    path('v1/common/', include('common.urls.v1')),
    path('v1/member/', include('member.urls.v1')),
    path('v1/order/', include('order.urls.v1')),
    path('v1/product/', include('product.urls.v1')),
    path('v1/payment/', include('payment.urls.v1')),
    path('v1/promotion/', include('promotion.urls.v1')),
]


if settings.DEBUG:
    import debug_toolbar

    urlpatterns += [
        path('__debug__/', include(debug_toolbar.urls)),
    ]
