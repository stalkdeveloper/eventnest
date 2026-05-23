"""
apps/accounts/api_urls.py
"""
from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .api_views import (
    RegisterAPIView,
    LoginAPIView,
    LogoutAPIView,
    ProfileAPIView,
    PasswordChangeAPIView,
    ForgotPasswordAPIView,
    ResetPasswordAPIView,
    VerifyEmailAPIView,
    ResendVerificationAPIView,
    MeAPIView,
)

urlpatterns = [
    # ── Auth ──────────────────────────────────────────────────────────────
    path('auth/register/',          RegisterAPIView.as_view(),          name='api_register'),
    path('auth/login/',             LoginAPIView.as_view(),             name='api_login'),
    path('auth/logout/',            LogoutAPIView.as_view(),            name='api_logout'),
    path('auth/token/refresh/',     TokenRefreshView.as_view(),         name='api_token_refresh'),
    path('auth/me/',                MeAPIView.as_view(),                name='api_me'),

    # ── Profile ───────────────────────────────────────────────────────────
    path('auth/profile/',           ProfileAPIView.as_view(),           name='api_profile'),

    # ── Password ──────────────────────────────────────────────────────────
    path('auth/password/change/',   PasswordChangeAPIView.as_view(),    name='api_password_change'),
    path('auth/password/forgot/',   ForgotPasswordAPIView.as_view(),    name='api_password_forgot'),
    path('auth/password/reset/',    ResetPasswordAPIView.as_view(),     name='api_password_reset'),

    # ── Email Verification ────────────────────────────────────────────────
    path('auth/email/verify/',      VerifyEmailAPIView.as_view(),       name='api_email_verify'),
    path('auth/email/resend/',      ResendVerificationAPIView.as_view(),name='api_email_resend'),
]
