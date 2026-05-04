from django import forms
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from apps.accounts.models import CustomUser


# ────────────────────────────────────────────────────────────────
#  User forms
# ────────────────────────────────────────────────────────────────

class UserCreateForm(forms.ModelForm):
    password     = forms.CharField(widget=forms.PasswordInput(), min_length=8, label='Password')
    group        = forms.ModelChoiceField(queryset=Group.objects.all(), required=True, label='Role')
    account_type = forms.ChoiceField(choices=CustomUser.AccountType.choices,
                                     initial=CustomUser.AccountType.PLATFORM, label='Account Type')

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


class UserEditForm(forms.ModelForm):
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
    group = forms.ModelChoiceField(queryset=Group.objects.all(), label='Assign Role')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['group'].widget.attrs['class'] = 'inline-role-select'


# ────────────────────────────────────────────────────────────────
#  Category forms
# ────────────────────────────────────────────────────────────────

class CategoryForm(forms.Form):
    title       = forms.CharField(max_length=100)
    slug        = forms.SlugField(max_length=120, required=False,
                                  help_text='Leave blank to auto-generate from title')
    parent      = forms.IntegerField(required=False, label='Parent Category (optional)')
    description = forms.CharField(widget=forms.Textarea(attrs={'rows': 3}), required=False)
    color       = forms.CharField(max_length=7, initial='#6366f1',
                                  widget=forms.TextInput(attrs={'type': 'color'}))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for f in self.fields.values():
            f.widget.attrs['class'] = 'form-input'


# ────────────────────────────────────────────────────────────────
#  Event forms (panel - admin creates/edits any event)
# ────────────────────────────────────────────────────────────────

class PanelEventForm(forms.Form):
    title        = forms.CharField(max_length=255)
    description  = forms.CharField(widget=forms.Textarea(attrs={'rows': 5}))
    category     = forms.IntegerField(required=False, label='Category ID (optional)')
    event_type   = forms.ChoiceField(choices=[
        ('offline', 'Offline'), ('online', 'Online'), ('hybrid', 'Hybrid')
    ])
    status       = forms.ChoiceField(choices=[
        ('draft', 'Draft'), ('published', 'Published'),
        ('cancelled', 'Cancelled'), ('completed', 'Completed'),
    ])
    start_date   = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        input_formats=['%Y-%m-%dT%H:%M'],
    )
    end_date     = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        input_formats=['%Y-%m-%dT%H:%M'],
    )
    venue        = forms.CharField(max_length=255, required=False)
    city         = forms.CharField(max_length=100, required=False)
    address      = forms.CharField(widget=forms.Textarea(attrs={'rows': 2}), required=False)
    online_link  = forms.URLField(required=False)
    max_capacity = forms.IntegerField(min_value=0, initial=0,
                                      help_text='0 = unlimited')
    ticket_price = forms.DecimalField(max_digits=10, decimal_places=2, initial=0.00)
    is_free      = forms.BooleanField(required=False, initial=True)
    is_featured  = forms.BooleanField(required=False)
    organiser_id = forms.IntegerField(required=False, label='Organiser User ID (optional)')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, f in self.fields.items():
            if not isinstance(f.widget, forms.CheckboxInput):
                f.widget.attrs['class'] = 'form-input'


class EventStatusForm(forms.Form):
    status = forms.ChoiceField(choices=[
        ('draft', 'Draft'), ('published', 'Published'),
        ('cancelled', 'Cancelled'), ('completed', 'Completed'),
    ])

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['status'].widget.attrs['class'] = 'inline-role-select'


# ────────────────────────────────────────────────────────────────
#  Role / Group forms (full CRUD)
# ────────────────────────────────────────────────────────────────

def _get_grouped_permissions():
    """Return permissions grouped by app label for the multi-select."""
    return Permission.objects.select_related('content_type').order_by(
        'content_type__app_label', 'codename'
    )


class RoleForm(forms.Form):
    name        = forms.CharField(max_length=150, label='Role Name')
    permissions = forms.ModelMultipleChoiceField(
        queryset=_get_grouped_permissions(),
        required=False,
        widget=forms.CheckboxSelectMultiple(),
        label='Permissions',
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['name'].widget.attrs['class'] = 'form-input'
