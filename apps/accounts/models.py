from django.contrib.auth.models import AbstractUser, Group
from django.db import models


class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    bio = models.TextField(blank=True, null=True)
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'

    def __str__(self):
        return self.email

    def get_profile_picture(self):
        from apps.media.models import Media
        return Media.objects.filter(
            mediable_type='accounts.CustomUser',
            mediable_id=self.pk,
            source_type='profile_picture'
        ).first()

    @property
    def role(self):
        group = self.groups.first()
        return group.name if group else 'Guest'

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)
        if is_new and not self.is_superuser:
            guest_group, _ = Group.objects.get_or_create(name='Guest')
            self.groups.add(guest_group)
