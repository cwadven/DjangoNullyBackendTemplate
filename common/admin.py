from common.models import (
    BlackListSection,
    BlackListWord,
)
from django.contrib import admin


class BlackListSectionAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'name',
    ]


class BlackListWordAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'wording',
        'black_list_section',
    ]


admin.site.register(BlackListSection, BlackListSectionAdmin)
admin.site.register(BlackListWord, BlackListWordAdmin)
