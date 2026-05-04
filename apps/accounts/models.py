from django.contrib.auth.models import AbstractUser, Group
from django.db import models


class CustomUser(AbstractUser):

    class AccountType(models.TextChoices):
        PLATFORM = 'platform', 'Platform'   # regular users & organisers
        SYSTEM   = 'system',   'System'     # admins & sub-admins

    email        = models.EmailField(unique=True)
    phone        = models.CharField(max_length=20, blank=True, null=True)
    bio          = models.TextField(blank=True, null=True)
    is_verified  = models.BooleanField(default=False)
    account_type = models.CharField(
        max_length=10,
        choices=AccountType.choices,
        default=AccountType.PLATFORM,
    )
    created_at   = models.DateTimeField(auto_now_add=True)
    updated_at   = models.DateTimeField(auto_now=True)

    USERNAME_FIELD  = 'email'
    REQUIRED_FIELDS = ['username']

    class Meta:
        verbose_name        = 'User'
        verbose_name_plural = 'Users'

    def __str__(self):
        return self.email

    # ── helpers ─────────────────────────────────────────────────────────

    @property
    def is_system_user(self):
        """True for admins and sub-admins (system account type or is_staff)."""
        return self.account_type == self.AccountType.SYSTEM or self.is_staff

    @property
    def role(self):
        group = self.groups.first()
        return group.name if group else 'Guest'

    def get_profile_picture(self):
        from apps.media.models import Media
        return Media.objects.filter(
            mediable_type='accounts.CustomUser',
            mediable_id=self.pk,
            source_type='profile_picture',
        ).first()

    # ── auto-assign Guest group on first save ────────────────────────────

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)
        if is_new and not self.is_superuser and not self.groups.exists():
            guest_group, _ = Group.objects.get_or_create(name='Guest')
            self.groups.add(guest_group)
