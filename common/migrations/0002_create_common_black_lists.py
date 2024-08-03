from django.db import migrations


def forward(apps, schema_editor):
    BlackListSection = apps.get_model('common', 'BlackListSection')
    BlackListWord = apps.get_model('common', 'BlackListWord')

    # 블랙 리스트 섹션
    black_list_section, _ = BlackListSection.objects.get_or_create(
        name='닉네임',
        description='닉네임 생성 혹은 수정 시 블랙리스트에 등록된 단어가 포함되어 있으면 블랙리스트 처리됩니다.'
    )

    # 블랙 리스트 문구
    BlackListWord.objects.create(
        wording='비회원',
        black_list_section_id=black_list_section.id,
    )


def backward(apps, schema_editor):
    BlackListSection = apps.get_model('common', 'BlackListSection')
    BlackListWord = apps.get_model('common', 'BlackListWord')

    # 블랙 리스트 문구
    BlackListWord.objects.filter(
        name='닉네임',
    ).delete()

    # 블랙 리스트 섹션
    BlackListSection.objects.filter(
        wording='비회원',
    ).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('common', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(forward, backward)
    ]
