from django.db import migrations


def forward(apps, schema_editor):
    MemberProvider = apps.get_model('member', 'MemberProvider')
    MemberStatus = apps.get_model('member', 'MemberStatus')
    MemberType = apps.get_model('member', 'MemberType')

    # 회원가입 유형
    MemberProvider.objects.get_or_create(
        name='email',
        description='original user'
    )
    MemberProvider.objects.get_or_create(
        name='kakao',
        description='social login by kakao.'
    )
    MemberProvider.objects.get_or_create(
        name='naver',
        description='social login by naver.'
    )
    MemberProvider.objects.get_or_create(
        name='google',
        description='social login by google.'
    )

    # 회원 상태
    MemberStatus.objects.get_or_create(
        name='정상',
        description='정상적인 유저'
    )
    MemberStatus.objects.get_or_create(
        name='탈퇴',
        description='탈퇴한 유저'
    )
    MemberStatus.objects.get_or_create(
        name='정지',
        description='정지된 유저'
    )
    MemberStatus.objects.get_or_create(
        name='휴면',
        description='휴면상태인 유저 3개월 간 로그인 하지 않은 경우'
    )

    # 회원 권한
    MemberType.objects.get_or_create(
        name='관리자',
        description='관리자 입니다. (모든 권한을 가지고 있습니다.)'
    )
    MemberType.objects.get_or_create(
        name='운영자',
        description='운영자 입니다. (다른 사람의 글을 삭제 할 수 있는 권한을 가지고 있습니다.)'
    )
    MemberType.objects.get_or_create(
        name='일반',
        description='일반 사용자 입니다.'
    )


def backward(apps, schema_editor):
    MemberProvider = apps.get_model('member', 'MemberProvider')
    MemberStatus = apps.get_model('member', 'MemberStatus')
    MemberType = apps.get_model('member', 'MemberType')

    # 회원가입 유형
    MemberProvider.objects.filter(
        name__in=['email', 'kakao', 'naver', 'google']
    ).delete()

    # 회원 상태
    MemberStatus.objects.filter(
        name__in=['정상', '탈퇴', '정지', '휴면']
    ).delete()

    # 회원 권한
    MemberType.objects.filter(
        name__in=['관리자', '운영자', '일반']
    ).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('member', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(forward, backward)
    ]
