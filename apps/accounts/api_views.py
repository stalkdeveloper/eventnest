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
    refresh = RefreshToken.for_user(user)
    return {'access': str(refresh.access_token), 'refresh': str(refresh)}


def _send_verification(user):
    from django.core import signing
    from apps.core.email.mailer import Mailer
    token = signing.dumps(user.pk, salt='email-verification')
    try:
        Mailer.send_verification_email(user, token)
    except Exception:
        pass


def _send_password_reset(user):
    from django.core import signing
    from apps.core.email.mailer import Mailer
    token = signing.dumps(user.pk, salt='password-reset')
    try:
        Mailer.send_password_reset_email(user, token)
    except Exception:
        pass


class RegisterAPIView(APIView):
    """
    POST /api/v1/auth/register/
    Body: { username, email, password, confirm_password, phone (optional) }
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


class LoginAPIView(APIView):
    """POST /api/v1/auth/login/ — Body: { email, password }"""
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data, context={'request': request})
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        user = serializer.validated_data['user']
        return Response({'user': UserProfileSerializer(user).data, **_token_pair(user)})


class LogoutAPIView(APIView):
    """POST /api/v1/auth/logout/ — Body: { refresh }"""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        refresh_token = request.data.get('refresh')
        if not refresh_token:
            return Response({'detail': 'Refresh token is required.'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            RefreshToken(refresh_token).blacklist()
        except TokenError:
            return Response({'detail': 'Invalid or already blacklisted token.'}, status=status.HTTP_400_BAD_REQUEST)
        return Response({'message': 'Logged out successfully.'})


class ProfileAPIView(APIView):
    """GET/PUT /api/v1/auth/profile/"""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response(UserProfileSerializer(request.user).data)

    def put(self, request):
        serializer = ProfileUpdateSerializer(request.user, data=request.data, partial=True)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        serializer.save()
        return Response({'message': 'Profile updated.', 'user': UserProfileSerializer(request.user).data})


class PasswordChangeAPIView(APIView):
    """POST /api/v1/auth/password/change/ — Body: { old_password, new_password, confirm_password }"""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = PasswordChangeSerializer(data=request.data, context={'request': request})
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        serializer.save()
        return Response({'message': 'Password changed successfully.', **_token_pair(request.user)})


class ForgotPasswordAPIView(APIView):
    """POST /api/v1/auth/password/forgot/ — Body: { email }"""
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
            pass
        return Response({'message': 'If an account exists for this email, a reset link has been sent.'})


class ResetPasswordAPIView(APIView):
    """POST /api/v1/auth/password/reset/ — Body: { token, new_password, confirm_password }"""
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = ResetPasswordSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        user = serializer.save()
        return Response({'message': 'Password reset successful. You can now log in.', **_token_pair(user)})


class VerifyEmailAPIView(APIView):
    """POST /api/v1/auth/email/verify/ — Body: { token }"""
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = VerifyEmailSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        user = serializer.save()
        return Response({'message': 'Email verified successfully.', 'user': UserProfileSerializer(user).data})


class ResendVerificationAPIView(APIView):
    """POST /api/v1/auth/email/resend/"""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        if request.user.is_verified:
            return Response({'message': 'Email is already verified.'})
        _send_verification(request.user)
        return Response({'message': 'Verification email sent. Please check your inbox.'})


class MeAPIView(APIView):
    """GET /api/v1/auth/me/"""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response(UserProfileSerializer(request.user).data)
