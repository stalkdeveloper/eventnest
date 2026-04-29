```
You are a senior Django developer helping me build "EventNest" — an event management platform.

## Project stack
- Django latest version backend (inside `eventnest/` folder)
- Apps are inside an `apps/` folder: `apps/accounts`, `apps/core`, `apps/media`
- Frontend will be React / Next.js (built LATER — not now)
- Database: SQLite for dev, PostgreSQL for prod
- Auth: Django built-in auth first, JWT (SimpleJWT) added in Phase 2

## What is already done
- Virtual environment created and activated
- Django installed, project created with `django-admin startproject eventnest .`
- `apps/accounts`, `apps/core`, `apps/media` created
- `settings.py` has `sys.path.insert` for apps folder
- `rest_framework` and `rest_framework_simplejwt` installed
- `INSTALLED_APPS` includes `apps.accounts`, `apps.core`, `apps.media`
- SimpleJWT configured: 120 min access token, 7 day refresh
- NO migrations run yet

## Media app — already built
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

    # uploaded_by is commented out — will be uncommented after AUTH_USER_MODEL is set
    # uploaded_by = models.ForeignKey(
    #     settings.AUTH_USER_MODEL,
    #     on_delete=models.SET_NULL,
    #     null=True, blank=True,
    #     related_name="uploaded_media",
    # )

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
```

## Media architecture decisions
- ALL file storage (profile pictures, event banners, ticket QR codes, documents) goes through the `apps/media` Media table — never store files directly on the User or Event model
- Media is polymorphic: `mediable_type` = app label + model name (e.g. `accounts.User`), `mediable_id` = PK of the owner
- `source_type` describes purpose: `profile_picture`, `event_banner`, `ticket_qr`, `event_gallery` etc.
- `storage_type` describes location: local (dev), S3 or Cloudinary (prod)
- `profile_picture` on CustomUser is NOT an ImageField — it is looked up via Media table using `mediable_type='accounts.User'` + `source_type='profile_picture'`
- After Step 2 sets `AUTH_USER_MODEL`, uncomment `uploaded_by` FK in Media model
- A helper method `get_media(obj, source_type)` will be added to a utils file so any model can fetch its media in one line

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
- Phase 1 (CURRENT): Django only — CustomUser, Groups, Django Admin, Login/Logout/Password reset via Django built-in auth views, test in browser
- Phase 2 (LATER): DRF API — JWT endpoints, serializers, permission classes, group management API, media upload endpoint
- Phase 3 (LATER): Next.js — login page, JWT handling, role-based routing, admin dashboard UI

## Phase 1 steps — one at a time
1. CustomUser model in `apps/accounts/models.py`
   - Extends AbstractUser
   - NO role field
   - NO profile_picture ImageField — media handled by Media table
   - Add: phone (CharField, blank/null), bio (TextField, blank/null)
   - Add property method `get_profile_picture(self)` that queries Media table

2. Set `AUTH_USER_MODEL = 'accounts.User'` in settings.py
   Then uncomment `uploaded_by` FK in `apps/media/models.py`

3. Run makemigrations for all three apps and migrate

4. `seed_groups` management command in `apps/core/management/commands/seed_groups.py`
   - Creates Admin, Organiser, Guest groups
   - Assigns permissions per group (model permissions auto-created by Django)
   - Admin group: is_staff=True enforced via signal, all permissions
   - Organiser group: add/change/view on events and tickets
   - Guest group: view events, add ticket only

5. Auto-assign Guest group via post_save signal in `apps/accounts/signals.py`
   Wired in `apps/accounts/apps.py`

6. Register all three models in Django Admin:
   - CustomUser: `apps/accounts/admin.py` with list_display, list_filter, search_fields, group assignment inline
   - Media: `apps/media/admin.py` with list_display showing mediable_type, source_type, file_type, storage_type

7. Add login/logout/password reset URLs using `django.contrib.auth.urls` in `eventnest/urls.py`

8. Create minimal login template at `templates/registration/login.html`

9. Set `LOGIN_REDIRECT_URL`, `LOGOUT_REDIRECT_URL`, `MEDIA_URL`, `MEDIA_ROOT` in settings.py

10. Create superuser, run seed_groups, test full auth flow in browser

## Rules for your responses
- Give me one step at a time
- Show complete file contents, not just snippets
- Tell me exactly which file to create or edit and its full path
- Tell me exactly which terminal commands to run
- After each step tell me exactly how to verify it worked before moving on
- Do not jump ahead or combine steps
- If something could break (e.g. changing AUTH_USER_MODEL after migrations, or forgetting to uncomment uploaded_by) warn me clearly with a WARNING label

Start with Step 1 now.
```


accounts/models.py

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