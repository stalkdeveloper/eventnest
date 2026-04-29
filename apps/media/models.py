from django.db import models
from django.conf import settings


class Media(models.Model):
    class StorageType(models.TextChoices):
        LOCAL      = "local",      "Local Storage"
        S3         = "s3",         "Amazon S3"
        CLOUDINARY = "cloudinary", "Cloudinary"
        URL        = "url",        "External URL"

    class FileType(models.TextChoices):
        IMAGE    = "image",    "Image"
        VIDEO    = "video",    "Video"
        DOCUMENT = "document", "Document"
        AUDIO    = "audio",    "Audio"
        OTHER    = "other",    "Other"

    mediable_type = models.CharField(max_length=100)
    mediable_id   = models.PositiveIntegerField()
    source_type   = models.CharField(max_length=50, blank=True, null=True)
    storage_type  = models.CharField(max_length=20, choices=StorageType.choices, default=StorageType.LOCAL)
    file_path     = models.CharField(max_length=2048, blank=True, null=True)
    full_url      = models.URLField(max_length=2048, blank=True, null=True)
    original_file_name = models.CharField(max_length=255)
    file_type     = models.CharField(max_length=20, choices=FileType.choices, default=FileType.IMAGE)
    extension     = models.CharField(max_length=20)

    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name="uploaded_media",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name        = "Media"
        verbose_name_plural = "Media"
        indexes = [
            models.Index(fields=["mediable_type", "mediable_id"]),
            models.Index(fields=["source_type"]),
        ]

    def __str__(self):
        return f"{self.source_type} — {self.original_file_name} ({self.mediable_type}:{self.mediable_id})"