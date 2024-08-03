from django.contrib import admin
from promotion.models import (
    Banner,
    PromotionRule,
    PromotionTag,
)


class PromotionRuleAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'description',
        'displayable',
        'display_start_time',
        'display_end_time',
        'action_page',
        'target_pk',
        'target_type',
        'external_target_url',
    ]


class PromotionTagAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'name',
    ]


class BannerAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'promotion_rule',
        'title',
        'title_font_color',
        'description',
        'description_font_color',
        'background_color',
        'target_layer',
    ]


admin.site.register(PromotionRule, PromotionRuleAdmin)
admin.site.register(PromotionTag, PromotionTagAdmin)
admin.site.register(Banner, BannerAdmin)
