from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import CustomUser


def verify_email(request, token):
    from django.core import signing
    try:
        user_pk = signing.loads(token, salt='email-verification', max_age=86400)
    except signing.SignatureExpired:
        messages.error(request, 'Verification link expired. Request a new one.')
        return redirect('accounts:resend_verification')
    except signing.BadSignature:
        messages.error(request, 'Invalid verification link.')
        return redirect('accounts:login')
    try:
        user = CustomUser.objects.get(pk=user_pk)
    except CustomUser.DoesNotExist:
        messages.error(request, 'User not found.')
        return redirect('accounts:login')
    if user.is_verified:
        messages.info(request, 'Email already verified.')
        return redirect('web_dashboard:dashboard')
    user.is_verified = True
    user.save(update_fields=['is_verified'])
    messages.success(request, '✅ Email verified! All features are unlocked.')
    return redirect('web_dashboard:dashboard')


@login_required
def resend_verification(request):
    if request.user.is_verified:
        messages.info(request, 'Email already verified.')
        return redirect('web_dashboard:dashboard')
    from django.core import signing
    token = signing.dumps(request.user.pk, salt='email-verification')
    try:
        from apps.core.email.mailer import Mailer
        Mailer.send_verification_email(request.user, token)
        messages.success(request, 'Verification email sent! Check your inbox.')
    except Exception as e:
        messages.error(request, f'Could not send email: {e}')
    return redirect('accounts:profile')
