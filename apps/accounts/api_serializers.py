from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from rest_framework import serializers
from .models import CustomUser


class RegisterSerializer(serializers.ModelSerializer):
    password  = serializers.CharField(write_only=True, min_length=8)
    password2 = serializers.CharField(write_only=True)

    class Meta:
        model  = CustomUser
        fields = ['username', 'email', 'password', 'password2', 'phone']

    def validate_email(self, value):
        if CustomUser.objects.filter(email=value.lower()).exists():
            raise serializers.ValidationError('An account with this email already exists.')
        return value.lower()

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({'password2': 'Passwords do not match.'})
        try:
            validate_password(attrs['password'])
        except ValidationError as e:
            raise serializers.ValidationError({'password': list(e.messages)})
        return attrs

    def create(self, validated_data):
        validated_data.pop('password2')
        password = validated_data.pop('password')
        user = CustomUser(**validated_data)
        user.account_type = CustomUser.AccountType.PLATFORM
        user.is_verified  = False
        user.set_password(password)
        user.save()
        return user


class LoginSerializer(serializers.Serializer):
    email    = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        email    = attrs['email'].lower()
        password = attrs['password']
        user = authenticate(request=self.context.get('request'), username=email, password=password)
        if not user:
            raise serializers.ValidationError('Invalid email or password.')
        if not user.is_active:
            raise serializers.ValidationError('This account has been disabled.')
        attrs['user'] = user
        return attrs


class UserProfileSerializer(serializers.ModelSerializer):
    role        = serializers.CharField(read_only=True)
    is_verified = serializers.BooleanField(read_only=True)
    profile_pic = serializers.SerializerMethodField()

    class Meta:
        model  = CustomUser
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name',
            'phone', 'bio', 'is_verified', 'role',
            'account_type', 'date_joined', 'profile_pic',
        ]
        read_only_fields = ['email', 'account_type', 'date_joined']

    def get_profile_pic(self, obj):
        pic = obj.get_profile_picture()
        return pic.get_url() if pic else None


class ProfileUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model  = CustomUser
        fields = ['username', 'first_name', 'last_name', 'phone', 'bio']

    def validate_username(self, value):
        qs = CustomUser.objects.filter(username=value).exclude(pk=self.instance.pk)
        if qs.exists():
            raise serializers.ValidationError('This username is already taken.')
        return value


class PasswordChangeSerializer(serializers.Serializer):
    old_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True, min_length=8)
    new_password2 = serializers.CharField(write_only=True)

    def validate_old_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError('Current password is incorrect.')
        return value

    def validate(self, attrs):
        if attrs['new_password'] != attrs['new_password2']:
            raise serializers.ValidationError({'new_password2': 'New passwords do not match.'})
        try:
            validate_password(attrs['new_password'], self.context['request'].user)
        except ValidationError as e:
            raise serializers.ValidationError({'new_password': list(e.messages)})
        return attrs

    def save(self):
        user = self.context['request'].user
        user.set_password(self.validated_data['new_password'])
        user.save(update_fields=['password'])
        return user


class ForgotPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        return value.lower()

class ResetPasswordSerializer(serializers.Serializer):
    token        = serializers.CharField()
    new_password  = serializers.CharField(write_only=True, min_length=8)
    new_password2 = serializers.CharField(write_only=True)

    def validate(self, attrs):
        if attrs['new_password'] != attrs['new_password2']:
            raise serializers.ValidationError({'new_password2': 'Passwords do not match.'})
        # Verify token
        from django.core import signing
        try:
            user_pk = signing.loads(attrs['token'], salt='password-reset', max_age=3600)
        except signing.SignatureExpired:
            raise serializers.ValidationError({'token': 'Reset link has expired (1 hour limit).'})
        except signing.BadSignature:
            raise serializers.ValidationError({'token': 'Invalid reset token.'})
        try:
            attrs['user'] = CustomUser.objects.get(pk=user_pk)
        except CustomUser.DoesNotExist:
            raise serializers.ValidationError({'token': 'User not found.'})
        try:
            validate_password(attrs['new_password'], attrs['user'])
        except ValidationError as e:
            raise serializers.ValidationError({'new_password': list(e.messages)})
        return attrs

    def save(self):
        user = self.validated_data['user']
        user.set_password(self.validated_data['new_password'])
        user.save(update_fields=['password'])
        return user


class VerifyEmailSerializer(serializers.Serializer):
    token = serializers.CharField()

    def validate_token(self, value):
        from django.core import signing
        try:
            user_pk = signing.loads(value, salt='email-verification', max_age=86400)
        except signing.SignatureExpired:
            raise serializers.ValidationError('Verification link has expired (24 hour limit).')
        except signing.BadSignature:
            raise serializers.ValidationError('Invalid verification token.')
        try:
            self._user = CustomUser.objects.get(pk=user_pk)
        except CustomUser.DoesNotExist:
            raise serializers.ValidationError('User not found.')
        return value

    def save(self):
        self._user.is_verified = True
        self._user.save(update_fields=['is_verified'])
        return self._user
