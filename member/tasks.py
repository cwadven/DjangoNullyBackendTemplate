from common.common_utils import send_email
from config.celery import app


# send_welcome_email.apply_async(('cwadven@naver.com', 'nully')) 같이 사용
@app.task
def send_welcome_email(email: str, nickname: str = None) -> None:
    nickname = nickname if nickname else '사용자'
    send_email(
        '회원가입을 환영합니다.',
        'email/member/welcome_member.html',
        {'body': f'{nickname} 님 진심으로 환영합니다~!', 'message': '많은 밈을 확인해보세요!'},
        [email]
    )


@app.task
def send_one_time_token_email(email: str, one_time_token: str) -> None:
    send_email(
        title='[회원가입] 인증',
        html_body_content='email/member/one_time_token.html',
        payload={
            'body': '[인증번호]',
            'message': f'{one_time_token}'
        },
        to=[email]
    )
