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
    import yaml
    from rest_framework import permissions
    from drf_yasg.views import get_schema_view
    from drf_yasg import openapi

    # swagger.yaml 파일 로드
    with open('docs/Swagger/swagger.yaml', 'r', encoding='utf-8') as f:
        swagger_yaml = yaml.safe_load(f)

    info = swagger_yaml.get('info', {})
    schema_view = get_schema_view(
        openapi.Info(
            title=info.get('title', 'Checker API'),
            default_version=info.get('version', 'v1'),
            description=info.get('description', ''),
        ),
        url=swagger_yaml.get('servers', [{}])[0].get('url', ''),
        patterns=None,
        public=True,
        permission_classes=[permissions.AllowAny],
        generator_class=None,
    )

    urlpatterns += [
        path('__debug__/', include(debug_toolbar.urls)),
        path(
            'swagger/',
            schema_view.with_ui('swagger', cache_timeout=0),
            name='schema-swagger-ui',
        ),
        path(
            'swagger.yaml',
            TemplateView.as_view(
                template_name='swagger/swagger.yaml',
                content_type='text/yaml',
            ),
            name='schema-yaml',
        ),
    ]
