from django.contrib import admin
from order.models import (
    Order,
    OrderItem,
    OrderItemDiscount,
    OrderItemRefund,
    OrderItemStatusLog,
    OrderStatusLog,
)


class OrderItemInline(admin.StackedInline):
    model = OrderItem
    extra = 0

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


class OrderAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'guest_id',
        'member_id',
        'order_number',
        'tid',
        'status',
        'canceled_at',
        'succeeded_at',
        'refunded_at',
        'request_at',
    ]
    inlines = [OrderItemInline]

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


class OrderStatusLogAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'order',
        'status',
        'request_at',
    ]

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


class OrderItemAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'product_id',
        'product_type',
        'product_price',
        'discounted_price',
        'paid_price',
        'item_quantity',
        'status',
        'canceled_at',
        'succeeded_at',
        'refunded_at',
    ]

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


class OrderItemRefundAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'order_item',
        'refunded_price',
        'refunded_quantity',
        'is_deleted',
        'request_at',
    ]

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


class OrderItemStatusLogAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'order_item',
        'status',
        'request_at',
    ]

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


class OrderItemDiscountAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'order_item',
        'discount_pk',
        'discount_type',
        'discounted_price',
    ]

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


admin.site.register(Order, OrderAdmin)
admin.site.register(OrderStatusLog, OrderStatusLogAdmin)
admin.site.register(OrderItem, OrderItemAdmin)
admin.site.register(OrderItemRefund, OrderItemRefundAdmin)
admin.site.register(OrderItemStatusLog, OrderItemStatusLogAdmin)
admin.site.register(OrderItemDiscount, OrderItemDiscountAdmin)
