from django.db import models
from django.contrib.auth.models import AbstractUser


class CustomUser(AbstractUser):
    """
    Custom user model for EventNest.
    - No role field (roles handled via Django Groups)
    - No profile_picture field (media handled via Media table)
    """

    phone = models.CharField(max_length=20, blank=True, null=True)
    bio = models.TextField(blank=True, null=True)

    groups = models.ManyToManyField(
        "auth.Group",
        verbose_name="groups",
        blank=True,
        related_name="customuser_set",
        related_query_name="customuser",
    )
    user_permissions = models.ManyToManyField(
        "auth.Permission",
        verbose_name="user permissions",
        blank=True,
        related_name="customuser_set",
        related_query_name="customuser",
    )

    class Meta:
        verbose_name = "User"
        verbose_name_plural = "Users"

    def __str__(self):
        return self.email or self.username

    @property
    def get_profile_picture(self):
        """
        Returns the Media object for this user's profile picture, or None.
        Queries the Media table using polymorphic fields.
        """
        try:
            from apps.media.models import Media
            return Media.objects.filter(
                mediable_type="accounts.CustomUser",
                mediable_id=self.pk,
                source_type="profile_picture",
            ).first()
        except Exception:
            return None