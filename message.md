```
You are a Django developer helping me build "EventNest" - an event management platform.

## Project stack
- Django latest version backend (inside `eventnest/` folder)
- Apps are inside an `apps/` folder: `apps/accounts`, `apps/core`, `apps/media`
- Frontend will be follow as template html 
- Database: SQLite for dev, PostgreSQL/Sql for prod

## What is already done
- Virtual environment created and activated
- Django installed, project created with `django-admin startproject eventnest .`
- `apps/accounts`, `apps/core`, `apps/media` created
- `apps/media` will be in the use for the store the images and documents in one table and will get info using single table
- `settings.py` has `sys.path.insert` for apps folder
- `INSTALLED_APPS` includes `apps.accounts`, `apps.core`, `apps.media`
- NO migrations run yet

## Media app - already built
`apps/media/models.py` is already written. Here is the complete file:

```python
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

    """
    No need because we are storing the model id and and model name so in that model table we will keep column created_by, updated_by and deleted_by etc.
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name="uploaded_media",
    ) 
    """

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
        return f"{self.source_type} - {self.original_file_name} ({self.mediable_type}:{self.mediable_id})"
```

## Media architecture decisions
- ALL file storage (profile pictures, event banners, ticket QR codes, documents etc.) goes through the `apps/media` Media table - never store files directly on the User or Event model
- Media is polymorphic: `mediable_type` = app label + model name (e.g. `accounts.User`), `mediable_id` = PK of the owner
- `source_type` describes purpose: `profile_picture`, `event_banner`, `ticket_qr`, `event_gallery` etc.
- `storage_type` describes location: local (dev), S3 or Cloudinary (prod)
- `profile_picture` on CustomUser is NOT an ImageField - it is looked up via Media table using `mediable_type='accounts.User'` + `source_type='profile_picture'`
- A helper method `get_media(obj, source_type)` will be added to a utils file so any model can fetch its media in one line or using relationships

## Architecture decisions already made
- NO static `role` field on User - use Django's built-in Groups and Permissions
- Three groups: Admin, Organiser, Guest(If Admin need will create subadmin)
- Guest group: view events, add ticket (register for event) only
- New users auto-assigned to Guest group


## Design
- Default admin design should be change as modern design
- website design should be in the modern gradient color


## Seeder setup
for testing and groups permissions make seeder and I think for this make separate database apps so every seeder part will be in the database apps.


## Auth 
- Add login/logout/password reset URLs for both type of user such as regular user and admin/subadmin user.