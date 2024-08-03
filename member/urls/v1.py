from django.urls import path
from member.views import (
    GetOrCreateGuestTokenView,
    LoginView,
    RefreshTokenView,
    SignUpEmailTokenSendView,
    SignUpEmailTokenValidationEndView,
    SignUpValidationView,
    SocialLoginView,
    SocialSignUpView,
)

app_name = 'member'


urlpatterns = [
    path('login', LoginView.as_view(), name='normal_login'),
    path('social-login', SocialLoginView.as_view(), name='social_login'),
    path('refresh-token', RefreshTokenView.as_view(), name='refresh_token'),
    path('guest-token', GetOrCreateGuestTokenView.as_view(), name='guest_token'),

    path('social-sign-up', SocialSignUpView.as_view(), name='social_sign_up'),
    path('sign-up-validation', SignUpValidationView.as_view(), name='sign_up_validation'),
    path('sign-up-check', SignUpEmailTokenSendView.as_view(), name='sign_up_check'),
    path('sign-up-validate-token', SignUpEmailTokenValidationEndView.as_view(), name='sign_up_token_validation'),
]
