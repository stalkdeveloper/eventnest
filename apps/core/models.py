from django.db import models
from django.conf import settings
from django.utils import timezone


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)
    color = models.CharField(max_length=7, default='#6366f1')  # hex color
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = 'Categories'
        ordering = ['name']

    def __str__(self):
        return self.name


class Event(models.Model):
    class Status(models.TextChoices):
        DRAFT     = 'draft',     'Draft'
        PUBLISHED = 'published', 'Published'
        CANCELLED = 'cancelled', 'Cancelled'
        COMPLETED = 'completed', 'Completed'

    class EventType(models.TextChoices):
        ONLINE  = 'online',  'Online'
        OFFLINE = 'offline', 'Offline'
        HYBRID  = 'hybrid',  'Hybrid'

    organiser   = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='organised_events')
    title       = models.CharField(max_length=255)
    slug        = models.SlugField(unique=True, max_length=255)
    description = models.TextField()
    category    = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, related_name='events')
    event_type  = models.CharField(max_length=10, choices=EventType.choices, default=EventType.OFFLINE)
    status      = models.CharField(max_length=15, choices=Status.choices, default=Status.DRAFT)

    start_date  = models.DateTimeField()
    end_date    = models.DateTimeField()
    venue       = models.CharField(max_length=255, blank=True)
    city        = models.CharField(max_length=100, blank=True)
    address     = models.TextField(blank=True)
    online_link = models.URLField(blank=True)

    max_capacity    = models.PositiveIntegerField(default=0)  # 0 = unlimited
    ticket_price    = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    is_free         = models.BooleanField(default=True)
    is_featured     = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-start_date']

    def __str__(self):
        return self.title

    def get_banner(self):
        from apps.media.models import Media
        return Media.objects.filter(
            mediable_type='core.Event',
            mediable_id=self.pk,
            source_type='event_banner'
        ).first()

    def get_gallery(self):
        from apps.media.models import Media
        return Media.objects.filter(
            mediable_type='core.Event',
            mediable_id=self.pk,
            source_type='event_gallery'
        )

    @property
    def tickets_sold(self):
        return self.tickets.filter(status='confirmed').count()

    @property
    def is_upcoming(self):
        return self.start_date > timezone.now()

    @property
    def spots_left(self):
        if self.max_capacity == 0:
            return None
        return max(0, self.max_capacity - self.tickets_sold)


class Ticket(models.Model):
    class Status(models.TextChoices):
        PENDING   = 'pending',   'Pending'
        CONFIRMED = 'confirmed', 'Confirmed'
        CANCELLED = 'cancelled', 'Cancelled'
        ATTENDED  = 'attended',  'Attended'

    event       = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='tickets')
    attendee    = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='tickets')
    ticket_code = models.CharField(max_length=20, unique=True)
    status      = models.CharField(max_length=15, choices=Status.choices, default=Status.CONFIRMED)
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    notes       = models.TextField(blank=True)
    registered_at = models.DateTimeField(auto_now_add=True)
    updated_at    = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['event', 'attendee']
        ordering = ['-registered_at']

    def __str__(self):
        return f"{self.ticket_code} - {self.attendee.email} @ {self.event.title}"

    def get_qr(self):
        from apps.media.models import Media
        return Media.objects.filter(
            mediable_type='core.Ticket',
            mediable_id=self.pk,
            source_type='ticket_qr'
        ).first()
