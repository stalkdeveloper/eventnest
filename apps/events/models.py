from django.db import models
from django.conf import settings
from django.utils import timezone
from django.utils.text import slugify
from apps.core.mixins import TimeStampedModel, ActiveManager, AllObjectsManager
from apps.categories.models import Category


class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(unique=True, max_length=60)
    color = models.CharField(max_length=7, default='#6366f1')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True,
        on_delete=models.SET_NULL, related_name='events_tag_created'
    )
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True,
        on_delete=models.SET_NULL, related_name='events_tag_updated'
    )
    deleted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True,
        on_delete=models.SET_NULL, related_name='events_tag_deleted'
    )

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def soft_delete(self, user=None):
        from django.utils import timezone as tz
        self.deleted_at = tz.now()
        self.deleted_by = user
        self.save(update_fields=['deleted_at', 'deleted_by', 'updated_at'])

    def restore(self):
        self.deleted_at = None
        self.deleted_by = None
        self.save(update_fields=['deleted_at', 'deleted_by', 'updated_at'])


class Event(TimeStampedModel):
    class Status(models.TextChoices):
        DRAFT = 'draft', 'Draft'
        PUBLISHED = 'published', 'Published'
        CANCELLED = 'cancelled', 'Cancelled'
        COMPLETED = 'completed', 'Completed'

    class EventType(models.TextChoices):
        ONLINE = 'online', 'Online'
        OFFLINE = 'offline', 'Offline'
        HYBRID = 'hybrid', 'Hybrid'

    organiser = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='organised_events',
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='events',
    )
    title = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, max_length=255)
    description = models.TextField()
    event_type = models.CharField(max_length=10, choices=EventType.choices, default=EventType.OFFLINE)
    status = models.CharField(max_length=15, choices=Status.choices, default=Status.DRAFT)

    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    venue = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=100, blank=True)
    address = models.TextField(blank=True)
    online_link = models.URLField(blank=True)

    max_capacity = models.PositiveIntegerField(default=0)  # 0 = unlimited
    ticket_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    is_free = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)

    tags = models.ManyToManyField('Tag', blank=True, related_name='events')

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='%(app_label)s_%(class)s_created'
    )
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='%(app_label)s_%(class)s_updated'
    )
    deleted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='%(app_label)s_%(class)s_deleted'
    )

    objects = ActiveManager()
    all_objects = AllObjectsManager()

    class Meta:
        ordering = ['-start_date']
        indexes = [
            models.Index(fields=['status', 'start_date']),
            models.Index(fields=['organiser', 'status']),
            models.Index(fields=['is_featured', 'status']),
            models.Index(fields=['is_free', 'status']),
            models.Index(fields=['city']),
        ]

    def __str__(self):
        return self.title

    def get_banner(self):
        from apps.media.models import Media
        return Media.objects.filter(
            mediable_type='events.Event',
            mediable_id=self.pk,
            source_type='event_banner',
        ).first()

    def get_gallery(self):
        from apps.media.models import Media
        return Media.objects.filter(
            mediable_type='events.Event',
            mediable_id=self.pk,
            source_type='event_gallery',
        )

    @property
    def tickets_sold(self):
        from apps.tickets.models import Ticket
        return Ticket.objects.filter(event=self, status='confirmed').count()

    @property
    def is_upcoming(self):
        return self.start_date > timezone.now()

    @property
    def spots_left(self):
        if self.max_capacity == 0:
            return None
        return max(0, self.max_capacity - self.tickets_sold)

# ── Feature 4: Wishlist ───────────────────────────────────────────────────────
class Wishlist(models.Model):
    user       = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='wishlisted_events')
    event      = models.ForeignKey('Event', on_delete=models.CASCADE, related_name='wishlisted_by')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['user', 'event']
        ordering        = ['-created_at']

    def __str__(self):
        return f'{self.user.email} → {self.event.title}'


# ── Feature 5: Review ─────────────────────────────────────────────────────────
class Review(models.Model):
    event      = models.ForeignKey('Event', on_delete=models.CASCADE, related_name='reviews')
    reviewer   = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='reviews')
    rating     = models.PositiveSmallIntegerField()
    body       = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['event', 'reviewer']
        ordering        = ['-created_at']

    def __str__(self):
        return f'{self.reviewer.username} → {self.event.title} ({self.rating}★)'
