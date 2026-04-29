You are a Django developer helping me build "EventNest" - an event management platform.

## Project stack
- Django latest version backend (inside `eventnest/` folder)
- Apps are inside an `apps/` folder: `apps/accounts`, `apps/core` and `apps/media`
- Frontend will be React / Next.js (built LATER — not now)
- Database: SQLite for dev, PostgreSQL for prod
- Auth: Django built-in auth first, JWT (SimpleJWT) added in Phase 2

## What is already done
- Virtual environment created and activated
- Django installed, project created with `django-admin startproject eventnest .`
- `apps/accounts`, `apps/core` and `apps/media` created
- `settings.py` has `sys.path.insert` for apps folder
- `rest_framework` and `rest_framework_simplejwt` installed
- `INSTALLED_APPS` includes `apps.accounts` and `apps.core`
- SimpleJWT configured: 120 min access token, 7 day refresh
- NO migrations run yet

## Architecture decisions already made
- NO static `role` field on User — use Django's built-in Groups and Permissions
- Three groups: Admin, Organiser, Guest
- Admin group: all permissions + manage users (is_staff=True)
- Organiser group: add/change/view events and tickets, no delete, no user management
- Guest group: view events, add ticket (register for event) only
- New users auto-assigned to Guest group via post_save signal
- Django Admin kept for superuser/developer use only
- React will have its own admin dashboard UI (Phase 3)
- JWT payload will include groups and permissions so React can read them

## Build phases
- Phase 1 (CURRENT): Django only — CustomUser, Groups, Django Admin, Login/Logout/Password reset via Django's built-in auth views, test in browser
- Phase 2 (LATER): DRF API — JWT endpoints, serializers, permission classes, group management API
- Phase 3 (LATER): Next.js — login page, JWT handling, role-based routing, admin dashboard UI

## Current task — Phase 1, step by step
We are building Phase 1 now. Guide me through each step one at a time, waiting for my confirmation before moving to the next. Steps are:

1. CustomUser model in `apps/accounts/models.py` (no role field, extends AbstractUser, adds phone and profile_picture)
2. Set `AUTH_USER_MODEL = 'accounts.User'` in settings.py
3. Run makemigrations and migrate
4. `seed_groups` management command in `apps/core/management/commands/seed_groups.py`
5. Auto-assign Guest group via post_save signal in `apps/accounts/signals.py`, wired in `apps/accounts/apps.py`
6. Register CustomUser in Django Admin with a clean ModelAdmin (list_display, list_filter, search_fields)
7. Add login/logout/password reset URLs using `django.contrib.auth.urls` in `eventnest/urls.py`
8. Create minimal login template at `templates/registration/login.html`
9. Set `LOGIN_REDIRECT_URL` and `LOGOUT_REDIRECT_URL` in settings.py
10. Create superuser and test full auth flow in browser

## Rules for your responses
- Give me one step at a time
- Show complete file contents, not just snippets
- Tell me exactly which file to create or edit
- Tell me exactly which terminal commands to run
- After each step, tell me how to verify it worked before moving on
- Do not jump ahead or combine steps
- If something could break (e.g. changing AUTH_USER_MODEL after migrations), warn me clearly

Start with Step 1 now.

D:\python\django\eventnest\apps\media\models.py
from django.db import models
from django.conf import settings


class Media(models.Model):
    """
    Polymorphic media table.
    Any model (User, Event, Ticket…) can own media records
    via mediable_type (e.g. 'accounts.User') + mediable_id (the object's PK).
    
    source_type  = PURPOSE  — why this file exists (profile picture, event banner…)
    storage_type = LOCATION — where the file physically lives (local, S3, Cloudinary…)
    """

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

    # --- Who owns this file (polymorphic) ---
    mediable_type = models.CharField(
        max_length=100,
        help_text="App label + model name of the owner, e.g. 'accounts.User'.",
    )
    mediable_id = models.PositiveIntegerField(
        help_text="Primary key of the owner object.",
    )

    source_type = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        help_text="What this file is used for, e.g. profile_picture, event_banner.",
    )

    storage_type = models.CharField(
        max_length=20,
        choices=StorageType.choices,
        default=StorageType.LOCAL,
        help_text="Storage backend where the file physically lives.",
    )
    file_path = models.CharField(
        max_length=2048,
        blank=True,
        null=True,
        help_text="Relative path on local disk or key on S3/Cloudinary.",
    )
    full_url = models.URLField(
        max_length=2048,
        blank=True,
        null=True,
        help_text="Absolute public or CDN URL to access the file.",
    )

    original_file_name = models.CharField(max_length=255)
    file_type = models.CharField(
        max_length=20,
        choices=FileType.choices,
        default=FileType.IMAGE,
    )
    extension = models.CharField(
        max_length=20,
        help_text="File extension without dot, e.g. 'jpg', 'pdf'.",
    )

    # --- Who uploaded it (uncomment after Step 2 sets AUTH_USER_MODEL) ---
    # uploaded_by = models.ForeignKey(
    #     settings.AUTH_USER_MODEL,
    #     on_delete=models.SET_NULL,
    #     null=True,
    #     blank=True,
    #     related_name="uploaded_media",
    # )

    # --- Timestamps ---
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
        return (
            f"{self.get_source_type_display()} — {self.original_file_name} "
            f"({self.mediable_type}:{self.mediable_id})"
        )