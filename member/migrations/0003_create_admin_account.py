from datetime import datetime

from django.db import migrations


def forward(apps, schema_editor):
    Member = apps.get_model('member', 'Member')
    member = Member.objects.create_superuser(
        username='admin',
        email='admin@admin.com',
        password='admin1q2w3e4r!',
    )
    member.member_type_id = 1
    member.member_status_id = 1
    member.member_provider_id = 1
    member.first_name = '관'
    member.last_name = '리자'
    member.nickname = 'admin'
    member.last_login = datetime.now()
    member.save()

    Guest = apps.get_model('member', 'Guest')
    Guest.objects.get_or_create(
        temp_nickname='관리자',
        ip='000.000.000.000',
        email='admin@admin.com',
        member_id=member.id,
    )


def backward(apps, schema_editor):
    Guest = apps.get_model('member', 'Guest')
    Guest.objects.filter(member__username='admin').delete()
    Member = apps.get_model('member', 'Member')
    Member.objects.filter(
        username='admin',
        is_superuser=True,
    ).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('member', '0002_create_account_constants'),
    ]

    operations = [
        migrations.RunPython(forward, backward)
    ]
