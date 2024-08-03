from django.contrib import admin
from member.models import (
    Guest,
    Member,
    MemberExtraLink,
    MemberInformation,
    MemberProvider,
    MemberStatus,
    MemberType,
)


class GuestAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'ip',
        'temp_nickname',
        'email',
        'member',
        'is_blacklisted',
        'last_joined_at',
    ]


class MemberAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'nickname',
        'member_type',
        'member_status',
        'member_provider',
    ]


class MemberProviderAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'name',
        'description'
    ]


class MemberStatusAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'name',
        'description'
    ]


class MemberTypeAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'name',
        'description'
    ]


class MemberInformationAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'member',
        'description',
        'is_deleted',
    ]


class MemberExtraLinkAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'member',
        'url',
        'title',
        'is_deleted',
    ]


admin.site.register(Guest, GuestAdmin)
admin.site.register(Member, MemberAdmin)
admin.site.register(MemberProvider, MemberProviderAdmin)
admin.site.register(MemberStatus, MemberStatusAdmin)
admin.site.register(MemberType, MemberTypeAdmin)
admin.site.register(MemberInformation, MemberInformationAdmin)
admin.site.register(MemberExtraLink, MemberExtraLinkAdmin)
