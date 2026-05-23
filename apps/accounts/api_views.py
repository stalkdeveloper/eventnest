"""
apps/accounts/api_views.py
Full Auth API — Register, Login, Logout, Profile, Password Change,
Forgot Password, Reset Password, Email Verification, Resend Verification.
"""
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError

from .models import CustomUser
from .api_serializers import (
    RegisterSerializer, LoginSerializer, UserProfileSerializer,
    ProfileUpdateSerializer, PasswordChangeSerializer,
    ForgotPasswordSerializer, ResetPasswordSerializer, VerifyEmailSerializer,
)


def _token_pair(user):
    """Return access + refresh tokens for a user."""
    refresh = RefreshToken.for_user(user)
    return {
        'access':  str(refresh.access_token),
        'refresh': str(refresh),
    }


def _send_verification(user):
    from django.core import signing
    from apps.core.email.mailer import Mailer
    token = signing.dumps(user.pk, salt='email-verification')
    try:
        Mailer.send_verification_email(user, token)
    except Exception:
        pass  # Never block register/resend because email fails


def _send_password_reset(user):
    from django.core import signing
    from apps.core.email.mailer import Mailer
    token = signing.dumps(user.pk, salt='password-reset')
    try:
        Mailer.send_password_reset_email(user, token)
    except Exception:
        pass


# ── Register ──────────────────────────────────────────────────────────────────
class RegisterAPIView(APIView):
    """
    POST /api/v1/auth/register/
    Body: { username, email, password, password2, phone (optional) }
    Returns: { user, access, refresh, message }
    """
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        user = serializer.save()
        _send_verification(user)

        return Response({
            'message': 'Account created. Please verify your email.',
            'user':    UserProfileSerializer(user).data,
            **_token_pair(user),
        }, status=status.HTTP_201_CREATED)


# ── Login ─────────────────────────────────────────────────────────────────────
class LoginAPIView(APIView):
    """
    POST /api/v1/auth/login/
    Body: { email, password }
    Returns: { user, access, refresh }
    """
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data, context={'request': request})
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        user = serializer.validated_data['user']
        return Response({
            'user':    UserProfileSerializer(user).data,
            **_token_pair(user),
        })


# ── Logout ────────────────────────────────────────────────────────────────────
class LogoutAPIView(APIView):
    """
    POST /api/v1/auth/logout/
    Header: Authorization: Bearer <access_token>
    Body: { refresh }
    Blacklists the refresh token so it can't be reused.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        refresh_token = request.data.get('refresh')
        if not refresh_token:
            return Response({'detail': 'Refresh token is required.'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            token = RefreshToken(refresh_token)
            token.blacklist()
        except TokenError:
            return Response({'detail': 'Invalid or already blacklisted token.'}, status=status.HTTP_400_BAD_REQUEST)
        return Response({'message': 'Logged out successfully.'})


# ── Token Refresh ─────────────────────────────────────────────────────────────
# Uses simplejwt's built-in view — registered in urls.py
# POST /api/v1/auth/token/refresh/
# Body: { refresh }
# Returns: { access }


# ── Profile ───────────────────────────────────────────────────────────────────
class ProfileAPIView(APIView):
    """
    GET  /api/v1/auth/profile/   → get my profile
    PUT  /api/v1/auth/profile/   → update username, first_name, last_name, phone, bio
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response(UserProfileSerializer(request.user).data)

    def put(self, request):
        serializer = ProfileUpdateSerializer(request.user, data=request.data, partial=True)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        serializer.save()
        return Response({
            'message': 'Profile updated.',
            'user':    UserProfileSerializer(request.user).data,
        })


# ── Password Change ───────────────────────────────────────────────────────────
class PasswordChangeAPIView(APIView):
    """
    POST /api/v1/auth/password/change/
    Header: Authorization: Bearer <access_token>
    Body: { old_password, new_password, new_password2 }
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = PasswordChangeSerializer(data=request.data, context={'request': request})
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        serializer.save()
        # Issue new tokens so old ones don't still work
        return Response({
            'message': 'Password changed successfully.',
            **_token_pair(request.user),
        })


# ── Forgot Password ───────────────────────────────────────────────────────────
class ForgotPasswordAPIView(APIView):
    """
    POST /api/v1/auth/password/forgot/
    Body: { email }
    Always returns 200 (security: don't reveal if email exists).
    Sends a reset link to the email if account exists.
    """
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = ForgotPasswordSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        email = serializer.validated_data['email']
        try:
            user = CustomUser.objects.get(email=email, is_active=True)
            _send_password_reset(user)
        except CustomUser.DoesNotExist:
            pass  # Silent — don't leak account existence

        return Response({
            'message': 'If an account exists for this email, a reset link has been sent.'
        })


# ── Reset Password ────────────────────────────────────────────────────────────
class ResetPasswordAPIView(APIView):
    """
    POST /api/v1/auth/password/reset/
    Body: { token, new_password, new_password2 }
    Token comes from the email link.
    """
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = ResetPasswordSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        user = serializer.save()
        return Response({
            'message': 'Password reset successful. You can now log in.',
            **_token_pair(user),
        })


# ── Email Verification ────────────────────────────────────────────────────────
class VerifyEmailAPIView(APIView):
    """
    POST /api/v1/auth/email/verify/
    Body: { token }   (token from verification email link)
    """
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = VerifyEmailSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        user = serializer.save()
        return Response({
            'message': 'Email verified successfully.',
            'user':    UserProfileSerializer(user).data,
        })


# ── Resend Verification Email ─────────────────────────────────────────────────
class ResendVerificationAPIView(APIView):
    """
    POST /api/v1/auth/email/resend/
    Header: Authorization: Bearer <access_token>
    Resends verification email if not already verified.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        if request.user.is_verified:
            return Response({'message': 'Email is already verified.'})
        _send_verification(request.user)
        return Response({'message': 'Verification email sent. Please check your inbox.'})


# ── Me (quick current-user check) ────────────────────────────────────────────
class MeAPIView(APIView):
    """
    GET /api/v1/auth/me/
    Header: Authorization: Bearer <access_token>
    Quick endpoint to check who is logged in and token validity.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response(UserProfileSerializer(request.user).data)
