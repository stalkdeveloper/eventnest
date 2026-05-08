from django.db import models
from django.conf import settings
from apps.core.mixins import TimeStampedModel, ActiveManager, AllObjectsManager


class Ticket(TimeStampedModel):
    class Status(models.TextChoices):
        PENDING   = 'pending',   'Pending'
        CONFIRMED = 'confirmed', 'Confirmed'
        CANCELLED = 'cancelled', 'Cancelled'
        ATTENDED  = 'attended',  'Attended'

    event = models.ForeignKey(
        'events.Event',
        on_delete=models.CASCADE,
        related_name='tickets'
    )
    attendee = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='tickets',
    )
    ticket_code = models.CharField(max_length=20, unique=True)
    status = models.CharField(max_length=15, choices=Status.choices, default=Status.CONFIRMED)
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    notes = models.TextField(blank=True)

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
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(blank=True, null=True)

    objects = ActiveManager()
    all_objects = AllObjectsManager()

    class Meta:
        unique_together = ['event', 'attendee']
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.ticket_code} - {self.attendee.email} @ {self.event.title}'

    def get_qr(self):
        from apps.media.models import Media
        return Media.objects.filter(
            mediable_type='tickets.Ticket',
            mediable_id=self.pk,
            source_type='ticket_qr',
        ).first()