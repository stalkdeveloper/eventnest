from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import Group
from .models import CustomUser


# ── Web forms ─────────────────────────────────────────────────────────────────

class RegisterForm(UserCreationForm):
    email    = forms.EmailField(required=True)
    username = forms.CharField()
    password1 = forms.CharField(
        label='Password',
        widget=forms.PasswordInput(attrs={'class': 'form-input', 'placeholder': 'Enter password'}),
        help_text='Minimum 8 characters.',
    )
    password2 = forms.CharField(
        label='Confirm Password',
        widget=forms.PasswordInput(attrs={'class': 'form-input', 'placeholder': 'Confirm password'}),
    )

    class Meta:
        model  = CustomUser
        fields = ['username', 'email', 'password1', 'password2']  # Django requires these names internally

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, f in self.fields.items():
            if 'class' not in f.widget.attrs:
                f.widget.attrs['class'] = 'form-input'


class LoginForm(AuthenticationForm):
    username = forms.EmailField(widget=forms.EmailInput(attrs={
        'class': 'form-input', 'placeholder': 'Email address', 'autofocus': True,
    }))
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-input', 'placeholder': 'Password',
    }))


class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model  = CustomUser
        fields = ['username', 'first_name', 'last_name', 'email', 'phone', 'bio']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-input'
            if name == 'bio':
                field.widget = forms.Textarea(attrs={'class': 'form-input', 'rows': 3})


# ── Admin forms ───────────────────────────────────────────────────────────────

class AdminUserCreateForm(forms.ModelForm):
    password     = forms.CharField(
        label='Password',
        widget=forms.PasswordInput(attrs={'class': 'form-input'}),
        min_length=8,
    )
    group        = forms.ModelChoiceField(queryset=Group.objects.all(), required=True, label='Role')
    account_type = forms.ChoiceField(choices=CustomUser.AccountType.choices,
                                     initial=CustomUser.AccountType.PLATFORM)

    class Meta:
        model  = CustomUser
        fields = ['username', 'email', 'first_name', 'last_name', 'phone', 'account_type']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for f in self.fields.values():
            f.widget.attrs['class'] = 'form-input'

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])
        if self.cleaned_data['account_type'] == CustomUser.AccountType.SYSTEM:
            user.is_staff = True
        if commit:
            user.save()
            user.groups.set([self.cleaned_data['group']])
        return user


class AdminUserEditForm(forms.ModelForm):
    group = forms.ModelChoiceField(queryset=Group.objects.all(), required=True, label='Role / Group')

    class Meta:
        model  = CustomUser
        fields = ['username', 'email', 'first_name', 'last_name',
                  'phone', 'account_type', 'is_verified', 'is_active']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk:
            current = self.instance.groups.first()
            if current:
                self.fields['group'].initial = current.pk
        for f in self.fields.values():
            f.widget.attrs['class'] = 'form-input'

    def save(self, commit=True):
        user = super().save(commit=False)
        user.is_staff = (self.cleaned_data['account_type'] == CustomUser.AccountType.SYSTEM)
        if commit:
            user.save()
            user.groups.set([self.cleaned_data['group']])
        return user


class AssignRoleForm(forms.Form):
    group = forms.ModelChoiceField(queryset=Group.objects.all(), label='Role')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['group'].widget.attrs['class'] = 'inline-role-select'
