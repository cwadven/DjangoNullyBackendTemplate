from django.contrib import admin
from product.models import (
    GiveProduct,
    GiveProductLog,
    PointProduct,
    ProductImage,
    ProductTag,
)


class PointProductAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'title',
        'description',
        'price',
        'is_active',
        'start_time',
        'end_time',
        'total_quantity',
        'left_quantity',
        'is_sold_out',
        'is_deleted',
        'point',
    ]


class GiveProductAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'order_item_id',
        'guest_id',
        'product_pk',
        'product_type',
        'status',
    ]


class GiveProductLogAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'give_product',
        'status',
        'created_at',
    ]


class ProductTagAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'name',
    ]


class ProductImageAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'product_pk',
        'product_type',
        'image_url',
        'is_deleted',
    ]


admin.site.register(PointProduct, PointProductAdmin)
admin.site.register(GiveProduct, GiveProductAdmin)
admin.site.register(GiveProductLog, GiveProductLogAdmin)
admin.site.register(ProductTag, ProductTagAdmin)
admin.site.register(ProductImage, ProductImageAdmin)
