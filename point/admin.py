from django.contrib import admin
from point.models import GuestPoint


class GuestPointAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'guest',
        'point',
        'reason',
        'is_active',
    ]


admin.site.register(GuestPoint, GuestPointAdmin)
