from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """
    Custom user model for EventNest.
    Extends Django's AbstractUser — no role field.
    Roles are handled via Django Groups (Admin, Organiser, Guest).
    """

    phone = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        help_text="Optional contact phone number.",
    )
    profile_picture = models.ImageField(
        upload_to="profile_pictures/",
        blank=True,
        null=True,
        help_text="Optional profile picture.",
    )

    class Meta:
        verbose_name = "User"
        verbose_name_plural = "Users"

    def __str__(self):
        return self.email or self.username